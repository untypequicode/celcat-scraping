# celcat-to-ics — backend

API FastAPI qui transforme un calendrier Celcat (groupe, matière ou salle) en
flux ICS standard, consommable par n'importe quel client de calendrier
(Google Calendar, Outlook, Apple Calendar, Thunderbird, abonnement
`webcal://`, etc.).

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

| Paramètre       | Requis | Défaut                             | Description                                                                          |
| --------------- | ------ | ---------------------------------- | ------------------------------------------------------------------------------------ |
| `resource_type` | Non    | `group`                            | Type de ressource : `group`, `module` (matière) ou `room` (salle).                   |
| `resource_id`   | Non*   | `CELCAT_DEFAULT_GROUP`             | Identifiant exact de la ressource (federation id) Celcat.                            |
| `group`         | Non    | —                                  | Alias historique de `resource_id` (rétrocompatibilité), utilisé seulement si absent. |
| `start`         | Non    | Aujourd'hui                        | Date de début (`YYYY-MM-DD`).                                                        |
| `end`           | Non    | `start + DEFAULT_RANGE_DAYS` jours | Date de fin (`YYYY-MM-DD`).                                                          |
| `base_url`      | Non    | `CELCAT_BASE_URL`                  | URL de base de l'instance Celcat (sans slash final).                                 |
| `cookie`        | Non*   | `CELCAT_COOKIE`                    | Cookie de session Celcat.                                                            |
| `calendar_name` | Non    | valeur de `resource_id`            | Nom affiché du calendrier (`X-WR-CALNAME`).                                          |
| `disposition`   | Non    | `inline`                           | `inline` ou `attachment` (en-tête `Content-Disposition`).                            |
| `no_cache`      | Non    | `false`                            | Si `true`, ignore le cache et force une nouvelle récupération.                       |

\* `resource_id` et `cookie` sont requis au global : soit fournis dans l'URL,
soit configurés côté serveur via `CELCAT_DEFAULT_GROUP` / `CELCAT_COOKIE`
(`CELCAT_DEFAULT_GROUP` ne s'applique que si `resource_type=group`).

### Trouver l'identifiant d'une ressource

Dans l'URL du calendrier Celcat affiché par le navigateur, ex :

```
https://celcat.u-bordeaux.fr/calendar/cal?vt=agendaWeek&dt=2026-09-06&et=module&fid0=4TBI702U
```

- `et` → le `resource_type` (`group`, `module` ou `room`)
- `fid0` → le `resource_id` (à décoder l'URL-encodage, ex: `A22%2F%20Salle%20201` → `A22/ Salle 201`)

### Exemples

Groupe :

```
GET /calendar.ics?resource_type=group&resource_id=M1%20CMI%20OSIA%20parcours%20OPTIM&start=2026-09-01&end=2026-12-31&cookie=...
```

Matière :

```
GET /calendar.ics?resource_type=module&resource_id=4TBI702U&start=2026-09-01&end=2026-12-31&cookie=...
```

Salle :

```
GET /calendar.ics?resource_type=room&resource_id=A22%2F%20Salle%20201&start=2026-09-01&end=2026-12-31&cookie=...
```

Avec un serveur déjà configuré (`CELCAT_DEFAULT_GROUP` et `CELCAT_COOKIE`
définis en environnement), l'URL minimale pour le groupe par défaut devient :

```
GET /calendar.ics
```

Cette URL peut être ajoutée directement comme abonnement de calendrier
(`webcal://` ou "Ajouter un calendrier depuis une URL") dans Google Calendar,
Outlook, Apple Calendar, etc.

### ⚠️ Si `module` ou `room` renvoie un calendrier vide

La correspondance entre `resource_type` et le code interne Celcat `resType`
est définie dans `app/celcat/client.py` (`RESOURCE_TYPE_CODES`). La valeur
`group = 103` a été confirmée via les DevTools du navigateur ; les valeurs
`room = 104` et `module = 105` sont des valeurs par convention non encore
vérifiées sur l'instance u-bordeaux.fr. Si une recherche par matière ou par
salle renvoie un calendrier vide alors que le lien Celcat correspondant
affiche bien des cours :

1. Ouvre le lien Celcat concerné (ex: un lien `et=module`) dans le navigateur, connecté.
2. Outils développeur (F12) → onglet Réseau → requête `GetCalendarData`.
3. Regarde la valeur du champ `resType` envoyé dans le corps de la requête.
4. Corrige la valeur correspondante dans `RESOURCE_TYPE_CODES`.

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
