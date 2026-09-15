use crate::AppState;
use anyhow::{anyhow, Result};
use chrono::{DateTime, Duration, NaiveDate, NaiveDateTime, TimeZone, Utc};
use icalendar::{Calendar, Component, Event, EventLike};
use regex::Regex;
use serde_json::Value;
use std::collections::HashMap;
use std::sync::OnceLock;
use tracing::info;
use percent_encoding::{utf8_percent_encode, NON_ALPHANUMERIC};
use chrono_tz::Europe::Paris;

fn resource_type_code(res_type: &str) -> &'static str {
    match res_type {
        "group" => "103",
        "room" => "104",
        "module" => "105",
        _ => "103",
    }
}

pub async fn generate_calendar(
    state: &AppState,
    base_url: &str,
    res_type: &str,
    res_id: &str,
    start: NaiveDate,
    end: NaiveDate,
    cookie: &str,
    cal_name: &str,
    custom_colors: Option<HashMap<String, String>>,
) -> Result<(Vec<u8>, Vec<String>)> {
    let mut current = start;
    let mut all_events = HashMap::new();
    let mut fetch_logs = Vec::new();

    let mut weeks = Vec::new();
    while current <= end {
        let week_end = std::cmp::min(current + Duration::days(6), end);
        weeks.push((current, week_end));
        current = week_end + Duration::days(1);
    }

    let total_weeks = weeks.len();
    for (i, (week_start, week_end)) in weeks.into_iter().enumerate() {
        info!("[{}/{}] Récupération {} -> {}", i + 1, total_weeks, week_start, week_end);

        match fetch_week(state, base_url, res_type, res_id, week_start, week_end, cookie).await {
            Ok(events) => {
                if let Some(arr) = events.as_array() {
                    for ev in arr {
                        all_events.insert(event_key(ev), ev.clone());
                    }
                }
            }
            Err(e) => {
                let msg = format!("ERREUR semaine {} -> {}: {}", week_start, week_end, e);
                fetch_logs.push(msg);
                if e.to_string().contains("401") || e.to_string().contains("403") {
                    return Err(e); // Erreur d'auth, on arrête tout
                }
            }
        }

        if i + 1 < total_weeks && state.config.request_sleep_seconds > 0.0 {
            tokio::time::sleep(tokio::time::Duration::from_secs_f32(state.config.request_sleep_seconds)).await;
        }
    }

    info!("{} événement(s) unique(s) récupéré(s)", all_events.len());

    let (cal, build_logs) = build_ics(all_events.values().collect(), cal_name, custom_colors);
    fetch_logs.extend(build_logs);

    Ok((cal.to_string().into_bytes(), fetch_logs))
}

async fn fetch_week(
    state: &AppState,
    base_url: &str,
    res_type: &str,
    res_id: &str,
    start: NaiveDate,
    end: NaiveDate,
    cookie: &str,
) -> Result<Value> {
    let url = format!("{}/Home/GetCalendarData", base_url);
    let end_exclusive = end + Duration::days(1);

    let form_data = [
        ("start", start.format("%Y-%m-%d").to_string()),
        ("end", end_exclusive.format("%Y-%m-%d").to_string()),
        ("resType", resource_type_code(res_type).to_string()),
        ("calView", "agendaWeek".to_string()),
        ("federationIds[]", res_id.to_string()),
        ("colourScheme", "3".to_string()),
    ];

    let origin = base_url.split("/calendar").next().unwrap_or(base_url);
    let encoded_id = utf8_percent_encode(res_id, NON_ALPHANUMERIC).to_string();
    let referer = format!("{}/cal?vt=agendaWeek&et={}&fid0={}", base_url, res_type, encoded_id);

    let resp = state.http_client.post(&url)
        .header("User-Agent", "Mozilla/5.0 (compatible; celcat-to-ics/1.0)")
        .header("Accept", "application/json, text/javascript, */*; q=0.01")
        .header("X-Requested-With", "XMLHttpRequest")
        .header("Cookie", cookie)
        .header("Origin", origin)
        .header("Referer", referer)
        .form(&form_data)
        .send()
        .await?;

    let status = resp.status();
    if status.is_client_error() || status.is_server_error() {
        return Err(anyhow!("Accès refusé ou erreur serveur (Statut {})", status));
    }

    let text = resp.text().await?;
    if text.trim().is_empty() {
        return Err(anyhow!("Réponse vide (Cookie expiré ?)"));
    }

    let json: Value = serde_json::from_str(&text)?;
    if let Some(events) = json.get("events") {
        Ok(events.clone())
    } else {
        Ok(json)
    }
}

// --- ICS & Parsing ---

static BLOCK_SEP_RE: OnceLock<Regex> = OnceLock::new();
static ITEM_SEP_RE: OnceLock<Regex> = OnceLock::new();

fn parse_celcat_blob(raw: &str) -> HashMap<&'static str, String> {
    let text = html_escape::decode_html_entities(raw).to_string();

    let block_re = BLOCK_SEP_RE.get_or_init(|| Regex::new(r"(?i)\n+\s*<br\s*/?>\s*\n+").unwrap());
    let item_re = ITEM_SEP_RE.get_or_init(|| Regex::new(r"(?i)\s*<br\s*/?>\s*").unwrap());

    let blocks: Vec<&str> = block_re.split(text.trim()).map(|s| s.trim()).collect();
    let mut result = HashMap::new();

    let split_items = |b: &str| -> String {
        item_re.split(b).map(|s| s.trim()).filter(|s| !s.is_empty()).collect::<Vec<_>>().join(", ")
    };

    if !blocks.is_empty() { result.insert("category", blocks[0].to_string()); }
    if blocks.len() > 1 { result.insert("title", blocks[1].to_string()); }
    if blocks.len() > 2 { result.insert("groups", split_items(blocks[2])); }
    if blocks.len() > 3 { result.insert("teachers", split_items(blocks[3])); }
    if blocks.len() > 4 { result.insert("room", blocks[4].to_string()); }
    if blocks.len() > 5 { result.insert("weeks", blocks[5].to_string()); }

    if blocks.len() > 6 {
        let notes = blocks[6..].join("\n");
        let clean_notes = notes.lines().map(|s| s.trim()).filter(|s| !s.is_empty()).collect::<Vec<_>>().join(" | ");
        result.insert("notes", clean_notes);
    }

    result
}

fn event_key(ev: &Value) -> String {
    if let Some(id) = ev.get("id") {
        if let Some(s) = id.as_str() { return s.to_string(); }
        return id.to_string();
    }
    use sha2::{Digest, Sha256};
    let raw = format!("{:?}|{:?}|{:?}", ev.get("start"), ev.get("end"), ev.get("description"));
    let mut hasher = Sha256::new();
    hasher.update(raw.as_bytes());
    hex::encode(hasher.finalize())[..16].to_string()
}

fn parse_dt(dt_str: &str) -> Option<DateTime<Utc>> {
    let clean = dt_str.replace('Z', "");

    if let Ok(naive_dt) = NaiveDateTime::parse_from_str(&clean, "%Y-%m-%dT%H:%M:%S") {
        return Some(Paris.from_local_datetime(&naive_dt).unwrap().with_timezone(&Utc));
    }

    if let Ok(naive_date) = NaiveDate::parse_from_str(&clean, "%Y-%m-%d") {
        let naive_dt = naive_date.and_hms_opt(0, 0, 0).unwrap();
        return Some(Paris.from_local_datetime(&naive_dt).unwrap().with_timezone(&Utc));
    }

    None
}

fn first_present<'a>(ev: &'a Value, keys: &[&str]) -> Option<&'a str> {
    for k in keys {
        if let Some(val) = ev.get(k).and_then(|v| v.as_str()) {
            if !val.is_empty() { return Some(val); }
        }
    }
    None
}

fn build_ics(events: Vec<&Value>, cal_name: &str, custom_colors: Option<HashMap<String, String>>) -> (Calendar, Vec<String>) {
    let mut cal = Calendar::new();
    cal.name(cal_name);
    cal.append_property(icalendar::Property::new("X-WR-TIMEZONE", "Europe/Paris"));

    let mut logs = Vec::new();
    let mut skipped = 0;

    for ev in events {
        let start_raw = ev.get("start").and_then(|v| v.as_str()).unwrap_or("");
        let end_raw = ev.get("end").and_then(|v| v.as_str());

        let start = match parse_dt(start_raw) {
            Some(dt) => dt,
            None => {
                logs.push(format!("IGNORÉ start invalide: {}", start_raw));
                skipped += 1;
                continue;
            }
        };

        let raw_blob = first_present(ev, &["description", "notes", "modules"]).unwrap_or("");
        let parsed = parse_celcat_blob(raw_blob);

        let category = parsed.get("category").cloned().or_else(|| first_present(ev, &["eventCategory"]).map(|s| s.to_string())).unwrap_or_default();
        let mut title = parsed.get("title").cloned().unwrap_or_default();
        if title.is_empty() { title = if category.is_empty() { "Cours".into() } else { category.clone() }; }

        let location = first_present(ev, &["sites", "rooms", "room"]).map(|s| s.to_string()).or_else(|| parsed.get("room").cloned()).unwrap_or_default();

        let mut desc_lines = Vec::new();
        if category != title && !category.is_empty() { desc_lines.push(format!("Type: {}", category)); }
        if let Some(t) = parsed.get("teachers") { if !t.is_empty() { desc_lines.push(format!("Enseignant(s): {}", t)); } }
        if let Some(g) = parsed.get("groups") { if !g.is_empty() { desc_lines.push(format!("Groupe(s): {}", g)); } }
        if let Some(r) = parsed.get("room") { if r != &location && !r.is_empty() { desc_lines.push(format!("Salle: {}", r)); } }
        if let Some(w) = parsed.get("weeks") { if !w.is_empty() { desc_lines.push(format!("Semaines: {}", w)); } }
        if let Some(n) = parsed.get("notes") { if !n.is_empty() { desc_lines.push(format!("Remarques: {}", n)); } }
        if let Some(d) = ev.get("department") {
            let dept = d.as_array().map(|arr| arr.iter().filter_map(|v| v.as_str()).collect::<Vec<_>>().join(", ")).unwrap_or_else(|| d.as_str().unwrap_or("").to_string());
            if !dept.is_empty() { desc_lines.push(format!("Département: {}", dept)); }
        }

        let mut cal_ev = Event::new();
        cal_ev.summary(&title)
              .uid(&format!("{}@celcat-to-ics", event_key(ev)))
              .timestamp(Utc::now());

        if let Some(end) = end_raw.and_then(parse_dt) {
            cal_ev.starts(start).ends(end);
        } else {
            cal_ev.starts(start.naive_utc().date()).ends(start.naive_utc().date() + Duration::days(1));
        }

        if !location.is_empty() { cal_ev.location(&location); }
        if !desc_lines.is_empty() { cal_ev.description(&desc_lines.join("\n")); }

        if let Some(colors) = &custom_colors {
            if let Some(color) = colors.get(&category) {
                cal_ev.append_property(icalendar::Property::new("COLOR", color));
                cal_ev.append_property(icalendar::Property::new("X-APPLE-CALENDAR-COLOR", color));
            }
        }

        cal.push(cal_ev);
    }

    if skipped > 0 {
        tracing::warn!("{} événement(s) ignoré(s) lors de la génération de l'ICS.", skipped);
    }

    (cal, logs)
}
