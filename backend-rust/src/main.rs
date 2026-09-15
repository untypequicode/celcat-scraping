use axum::{
    extract::{Query, State},
    http::{header, HeaderMap, StatusCode},
    response::{IntoResponse, Response},
    routing::get,
    Router,
};
use chrono::{Duration, NaiveDate, Utc};
use moka::future::Cache;
use serde::Deserialize;
use std::sync::Arc;
use tokio::net::TcpListener;
use tower_http::cors::{Any, CorsLayer};
use tracing::{error, info, warn};

mod celcat;

#[derive(Deserialize, Clone)]
pub struct Config {
    #[serde(default = "default_base_url")]
    pub celcat_base_url: String,
    pub celcat_cookie: Option<String>,
    pub celcat_default_group: Option<String>,
    #[serde(default = "default_range_days")]
    pub default_range_days: i64,
    #[serde(default = "default_sleep")]
    pub request_sleep_seconds: f32,
    #[serde(default = "default_timeout")]
    pub request_timeout_seconds: u64,
    #[serde(default = "default_cache_ttl")]
    pub cache_ttl_seconds: u64,
    #[serde(default = "default_cors")]
    pub cors_origins: String,
}

fn default_base_url() -> String { "https://celcat.u-bordeaux.fr/calendar".into() }
fn default_range_days() -> i64 { 90 }
fn default_sleep() -> f32 { 0.4 }
fn default_timeout() -> u64 { 20 }
fn default_cache_ttl() -> u64 { 300 }
fn default_cors() -> String { "*".into() }

// L'état partagé entre toutes les requêtes (Thread-safe)
pub struct AppState {
    pub config: Config,
    pub http_client: reqwest::Client,
    pub ics_cache: Cache<String, (Vec<u8>, Vec<String>)>,
}

#[derive(Deserialize)]
struct CalendarQuery {
    resource_type: Option<String>,
    resource_id: Option<String>,
    group: Option<String>,
    start: Option<NaiveDate>,
    end: Option<NaiveDate>,
    base_url: Option<String>,
    cookie: Option<String>,
    calendar_name: Option<String>,
    #[serde(default = "default_disposition")]
    disposition: String,
    #[serde(default)]
    no_cache: bool,
    colors: Option<String>,
}

fn default_disposition() -> String { "inline".into() }

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialisation des logs
    tracing_subscriber::fmt()
        .with_env_filter(tracing_subscriber::EnvFilter::from_default_env().add_directive("celcat_to_ics=info".parse()?))
        .init();

    let _ = dotenvy::dotenv(); // Charge .env si présent
    let config: Config = envy::from_env()?;

    let http_client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(config.request_timeout_seconds))
        .build()?;

    let cache = Cache::builder()
        .time_to_live(std::time::Duration::from_secs(config.cache_ttl_seconds))
        .build();

    let state = Arc::new(AppState {
        config: config.clone(),
        http_client,
        ics_cache: cache,
    });

    let cors = if config.cors_origins == "*" {
        CorsLayer::new().allow_origin(Any).allow_methods(Any).allow_headers(Any)
    } else {
        CorsLayer::permissive() // Simplification pour le snippet, adaptable si besoin
    };

    let app = Router::new()
        .route("/", get(root_handler))
        .route("/health", get(health_handler))
        .route("/calendar.ics", get(calendar_handler))
        .layer(cors)
        .with_state(state);

    let addr = "0.0.0.0:8000";
    info!("Serveur démarré sur http://{}", addr);
    let listener = TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}

async fn root_handler() -> axum::Json<serde_json::Value> {
    axum::Json(serde_json::json!({
        "name": "celcat-to-ics (Rust)",
        "calendar_endpoint": "/calendar.ics"
    }))
}

async fn health_handler() -> axum::Json<serde_json::Value> {
    axum::Json(serde_json::json!({ "status": "ok" }))
}

async fn calendar_handler(
    State(state): State<Arc<AppState>>,
    Query(params): Query<CalendarQuery>,
) -> Result<Response, (StatusCode, String)> {
    let res_type = params.resource_type.unwrap_or_else(|| "group".into()).to_lowercase();
    if !["group", "module", "room"].contains(&res_type.as_str()) {
        return Err((StatusCode::BAD_REQUEST, "resource_type invalide".into()));
    }

    let default_id = if res_type == "group" { state.config.celcat_default_group.clone() } else { None };
    let res_id = params.resource_id.or(params.group).or(default_id).unwrap_or_default();
    if res_id.trim().is_empty() {
        return Err((StatusCode::BAD_REQUEST, "resource_id est requis".into()));
    }

    let cookie = params.cookie.or(state.config.celcat_cookie.clone()).unwrap_or_default();
    if cookie.trim().is_empty() {
        return Err((StatusCode::UNAUTHORIZED, "Cookie Celcat manquant".into()));
    }

    let start = params.start.unwrap_or_else(|| Utc::now().date_naive());
    let end = params.end.unwrap_or_else(|| start + Duration::days(state.config.default_range_days));

    if end < start {
        return Err((StatusCode::BAD_REQUEST, "end doit être postérieur ou égal à start".into()));
    }

    let base_url = params.base_url.unwrap_or(state.config.celcat_base_url.clone());
    let base_url = base_url.trim_end_matches('/');
    let cal_name = params.calendar_name.unwrap_or(res_id.clone());

    let custom_colors: Option<std::collections::HashMap<String, String>> = match params.colors {
        Some(ref c) => serde_json::from_str(c).map_err(|_| (StatusCode::BAD_REQUEST, "JSON colors invalide".into()))?,
        None => None,
    };

    // Création de la clé de cache
    use sha2::{Digest, Sha256};
    let mut hasher = Sha256::new();
    hasher.update(cookie.as_bytes());
    let cookie_hash = hex::encode(hasher.finalize())[..16].to_string();
    let cache_key = format!("{}|{}|{}|{}|{}|{}", base_url, res_type, res_id, start, end, cookie_hash);

    // Vérification du cache
    if !params.no_cache && state.config.cache_ttl_seconds > 0 {
        if let Some(cached) = state.ics_cache.get(&cache_key).await {
            info!("Cache hit pour resource_id={}", res_id);
            return build_response(&cached.0, &res_id, &params.disposition);
        }
    }

    // Récupération et conversion
    match celcat::generate_calendar(&state, base_url, &res_type, &res_id, start, end, &cookie, &cal_name, custom_colors).await {
        Ok((ics_bytes, log_lines)) => {
            for line in log_lines.iter() {
                warn!("{}", line);
            }
            if !params.no_cache && state.config.cache_ttl_seconds > 0 {
                state.ics_cache.insert(cache_key, (ics_bytes.clone(), log_lines)).await;
            }
            build_response(&ics_bytes, &res_id, &params.disposition)
        }
        Err(e) => {
            error!("Erreur génération Celcat: {}", e);
            Err((StatusCode::BAD_GATEWAY, e.to_string()))
        }
    }
}

fn build_response(ics_bytes: &[u8], res_id: &str, disposition: &str) -> Result<Response, (StatusCode, String)> {
    let filename = format!("{}.ics", res_id.replace('/', "-"));
    let mut headers = HeaderMap::new();
    headers.insert(header::CONTENT_TYPE, "text/calendar; charset=utf-8".parse().unwrap());
    headers.insert(header::CONTENT_DISPOSITION, format!("{}; filename=\"{}\"", disposition, filename).parse().unwrap());

    Ok((headers, ics_bytes.to_vec()).into_response())
}
