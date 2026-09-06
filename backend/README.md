# celcat-to-ics — backend

API FastAPI qui transforme le calendrier d'un groupe Celcat en flux ICS
standard, consommable par n'importe quel client de calendrier (Google
Calendar, Outlook, Apple Calendar, Thunderbird, abonnement `webcal://`, etc.).

## Authentification (important)

L'instance Celcat exige une authentification SSO (Shibboleth/SAML) pour
accéder aux données du calendrier, même pour un groupe. Cette API n'automatise
PAS le login. Il faut récupérer manuellement un cookie de session valide :

1. Connecte-toi normalement dans ton navigateur sur
   `https://celcat.u-bordeaux.fr/calendar/cal?...&fid0=TON_GROUPE` jusqu'à
   voir le calendrier s'afficher.
2. Ouvre les outils développeur (F12) > onglet Réseau (Network).
3. Recharge la page, trouve la requête `GetCalendarData`.
4. Dans l'onglet "En-têtes" de cette requête, copie la valeur complète du
   header `Cookie` (une longue chaîne `cle1=val1; cle2=val2; ...`).
5. Utilise cette valeur soit :
   - comme valeur de la variable d'environnement `CELCAT_COOKIE` (voir
     `.env.example`) pour l'utiliser par défaut sur toutes les requêtes,
   - soit en paramètre `cookie` directement dans l'URL d'appel.

Le cookie de session expire après un certain temps d'inactivité (souvent
20-60 min sur ASP.NET Core) : il faudra le renouveler périodiquement.

## Configuration

Copier `.env.example` en `.env` et adapter les valeurs (voir les commentaires
dans le fichier). Toutes les variables sont aussi utilisables directement en
variables d'environnement (pratique avec Docker).

## Lancer en local

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

L'API est alors disponible sur `http://localhost:8000`, avec une
documentation interactive sur `http://localhost:8000/docs`.

## Lancer avec Docker

```bash
docker build -t celcat-to-ics .
docker run --rm -p 8000:8000 --env-file .env celcat-to-ics
```

## Endpoint principal

```
GET /calendar.ics
```

| Paramètre       | Requis | Défaut                             | Description                                                    |
| --------------- | ------ | ---------------------------------- | -------------------------------------------------------------- |
| `group`         | Non*   | `CELCAT_DEFAULT_GROUP`             | Nom exact du groupe (federation id) Celcat.                    |
| `start`         | Non    | Aujourd'hui                        | Date de début (`YYYY-MM-DD`).                                  |
| `end`           | Non    | `start + DEFAULT_RANGE_DAYS` jours | Date de fin (`YYYY-MM-DD`).                                    |
| `base_url`      | Non    | `CELCAT_BASE_URL`                  | URL de base de l'instance Celcat (sans slash final).           |
| `cookie`        | Non*   | `CELCAT_COOKIE`                    | Cookie de session Celcat.                                      |
| `calendar_name` | Non    | valeur de `group`                  | Nom affiché du calendrier (`X-WR-CALNAME`).                    |
| `disposition`   | Non    | `inline`                           | `inline` ou `attachment` (en-tête `Content-Disposition`).      |
| `no_cache`      | Non    | `false`                            | Si `true`, ignore le cache et force une nouvelle récupération. |

\* `group` et `cookie` sont requis au global : soit fournis dans l'URL, soit
configurés côté serveur via `CELCAT_DEFAULT_GROUP` / `CELCAT_COOKIE`.

### Exemples

Avec cookie et groupe fournis directement dans l'URL :

```
GET /calendar.ics?group=M1%20CMI%20OSIA%20parcours%20OPTIM&start=2026-09-01&end=2026-12-31&cookie=ASP.NET_SessionId=...;
```

Avec un serveur déjà configuré (`CELCAT_DEFAULT_GROUP` et `CELCAT_COOKIE`
définis en environnement), l'URL minimale devient :

```
GET /calendar.ics
```

Cette URL peut être ajoutée directement comme abonnement de calendrier
(`webcal://` ou "Ajouter un calendrier depuis une URL") dans Google Calendar,
Outlook, Apple Calendar, etc.

## Autres endpoints

- `GET /health` — vérification de disponibilité.
- `GET /docs` — documentation interactive Swagger (générée par FastAPI).

## Structure du code

```
app/
├── main.py             # Application FastAPI et route /calendar.ics
├── service.py          # Orchestration : fetch Celcat + build ICS + cache
├── core/               # Infrastructure générique
│   ├── config.py       # Configuration (variables d'environnement)
│   ├── cache.py        # Cache en mémoire avec TTL
│   └── exceptions.py   # Exceptions dédiées (auth, erreurs génériques)
└── celcat/             # Tout ce qui touche à Celcat
    ├── client.py       # Appels HTTP à l'API Celcat (semaine par semaine)
    └── converter.py    # Parsing du bloc pseudo-HTML Celcat -> fichier ICS
```
