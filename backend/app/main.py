"""API FastAPI exposant un calendrier Celcat au format ICS.

Endpoint principal :

    GET /calendar.ics?group=...&start=YYYY-MM-DD&end=YYYY-MM-DD

Tous les paramètres sont surchargeables depuis l'URL ; ceux qui sont omis
retombent sur les valeurs par défaut définies via variables d'environnement
(cf. `app/core/config.py` et `.env.example`).
"""

import datetime as dt
import logging
from typing import Literal, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from .core.config import Settings, get_settings
from .core.exceptions import CelcatAuthError, CelcatError
from .service import generate_calendar_ics, resolve_request

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Celcat to ICS",
    description="Convertit un calendrier de groupe Celcat en flux ICS standard.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins_list,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/", tags=["meta"])
def root() -> dict:
    return {
        "name": "celcat-to-ics",
        "docs": "/docs",
        "calendar_endpoint": "/calendar.ics",
    }


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}


@app.get(
    "/calendar.ics",
    tags=["calendar"],
    summary="Génère le calendrier ICS d'un groupe Celcat",
    responses={
        200: {"content": {"text/calendar": {}}},
        400: {"description": "Paramètres invalides"},
        401: {"description": "Cookie de session Celcat manquant, invalide ou expiré"},
        502: {"description": "Erreur lors de la communication avec Celcat"},
    },
)
def get_calendar(
    group: Optional[str] = Query(
        default=None,
        description="Nom exact du groupe (federation id) Celcat, ex: 'M1 CMI OSIA parcours OPTIM'.",
    ),
    start: Optional[dt.date] = Query(
        default=None,
        description="Date de début (YYYY-MM-DD). Par défaut : aujourd'hui.",
    ),
    end: Optional[dt.date] = Query(
        default=None,
        description="Date de fin (YYYY-MM-DD). Par défaut : aujourd'hui + DEFAULT_RANGE_DAYS jours.",
    ),
    base_url: Optional[str] = Query(
        default=None,
        description="URL de base de l'instance Celcat (sans slash final).",
    ),
    cookie: Optional[str] = Query(
        default=None,
        description=(
            "Cookie de session Celcat (valeur complète du header Cookie). "
            "Si omis, le cookie configuré côté serveur (CELCAT_COOKIE) est utilisé."
        ),
    ),
    calendar_name: Optional[str] = Query(
        default=None,
        description="Nom affiché du calendrier (X-WR-CALNAME). Par défaut : le nom du groupe.",
    ),
    disposition: Literal["inline", "attachment"] = Query(
        default="inline",
        description="Contrôle l'en-tête Content-Disposition de la réponse.",
    ),
    no_cache: bool = Query(
        default=False,
        description="Si vrai, ignore le cache et force une nouvelle récupération depuis Celcat.",
    ),
    settings: Settings = Depends(get_settings),
) -> Response:
    try:
        req = resolve_request(
            group=group,
            start=start,
            end=end,
            base_url=base_url,
            cookie=cookie,
            calendar_name=calendar_name,
            settings=settings,
        )
    except CelcatAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        ics_bytes, log_lines = generate_calendar_ics(
            base_url=req.base_url,
            group=req.group,
            start=req.start,
            end=req.end,
            cookie=req.cookie,
            calendar_name=req.calendar_name,
            settings=settings,
            use_cache=not no_cache,
        )
    except CelcatAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except CelcatError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    for line in log_lines:
        logger.warning(line)

    filename = f"{req.group}.ics".replace("/", "-")
    return Response(
        content=ics_bytes,
        media_type="text/calendar; charset=utf-8",
        headers={"Content-Disposition": f'{disposition}; filename="{filename}"'},
    )
