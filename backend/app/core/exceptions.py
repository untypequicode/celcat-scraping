"""Exceptions spécifiques au scraping Celcat."""


class CelcatError(Exception):
    """Erreur générique lors de la récupération des données Celcat."""


class CelcatAuthError(CelcatError):
    """Le cookie de session Celcat est manquant, invalide ou expiré."""
