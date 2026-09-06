export type ResourceType = "group" | "module" | "room";

const VALID_RESOURCE_TYPES: ResourceType[] = ["group", "module", "room"];

export interface ParsedCelcatUrl {
  baseUrl: string;
  resourceType: ResourceType;
  resourceId: string;
  date: string | null;
}

export interface CelcatUrlParseResult {
  data: ParsedCelcatUrl | null;
  error: string | null;
}

/**
 * Extrait le type de ressource (groupe/matière/salle), son identifiant et
 * l'URL de base d'une instance Celcat à partir d'un lien copié depuis le
 * navigateur, ex:
 * https://celcat.u-bordeaux.fr/calendar/cal?vt=agendaWeek&et=group&fid0=GROUPE
 * https://celcat.u-bordeaux.fr/calendar/cal?vt=agendaWeek&et=module&fid0=4TBI702U
 * https://celcat.u-bordeaux.fr/calendar/cal?vt=agendaWeek&et=room&fid0=A22%2F%
20Salle%20201
 */
export function useCelcatUrlParser() {
  function parse(raw: string): CelcatUrlParseResult {
    if (!raw.trim()) {
      return { data: null, error: null };
    }

    let parsed: URL;
    try {
      parsed = new URL(raw.trim());
    } catch {
      return { data: null, error: "Ce n'est pas une URL valide." };
    }

    const resourceId = parsed.searchParams.get("fid0");
    if (!resourceId) {
      return {
        data: null,
        error:
          "Impossible de trouver la ressource (paramètre 'fid0') dans ce lien.",
      };
    }

    const rawType = parsed.searchParams.get("et") as ResourceType | null;
    const resourceType: ResourceType =
      rawType && VALID_RESOURCE_TYPES.includes(rawType) ? rawType : "group";

    // "https://.../calendar/cal?..." -> "https://.../calendar"
    const cleanedPath = parsed.pathname.replace(/\/cal\/?$/i, "");

    return {
      data: {
        baseUrl: `${parsed.origin}${cleanedPath}`,
        resourceType,
        resourceId,
        date: parsed.searchParams.get("dt"),
      },
      error: null,
    };
  }

  return { parse };
}
