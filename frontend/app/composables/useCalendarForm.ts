import type { ResourceType } from "~/composables/useCelcatUrlParser";

export type SourceMode = "url" | "manual";

const DEFAULT_BASE_URL = "https://celcat.u-bordeaux.fr/calendar";

const RESOURCE_TYPE_LABELS: Record<ResourceType, string> = {
  group: "Groupe",
  module: "Matière",
  room: "Salle",
};

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

function defaultEndIso(): string {
  const date = new Date();
  date.setDate(date.getDate() + 90);
  return date.toISOString().slice(0, 10);
}

/**
 * État + logique du formulaire de génération de lien calendrier.
 * Centralise tout ce qui est partagé entre les étapes du formulaire et le
 * panneau de résultat, pour que les composants restent surtout présentatifs.
 */
export function useCalendarForm() {
  const config = useRuntimeConfig();
  const apiBaseUrl = computed(() =>
    String(config.public.apiBaseUrl).replace(/\/$/, ""),
  );
  const { parse } = useCelcatUrlParser();

  const mode = ref<SourceMode>("url");

  // Source
  const celcatUrl = ref("");
  const baseUrl = ref(DEFAULT_BASE_URL);
  const resourceType = ref<ResourceType>("group");
  const resourceId = ref("");
  const urlError = ref("");
  const detected = ref<{
    baseUrl: string;
    resourceType: ResourceType;
    resourceId: string;
  } | null>(null);

  watch(celcatUrl, (raw) => {
    const result = parse(raw);
    urlError.value = result.error ?? "";
    detected.value = result.data
      ? {
          baseUrl: result.data.baseUrl,
          resourceType: result.data.resourceType,
          resourceId: result.data.resourceId,
        }
      : null;
    if (result.data) {
      baseUrl.value = result.data.baseUrl;
      resourceType.value = result.data.resourceType;
      resourceId.value = result.data.resourceId;
    }
  });

  // Période (toujours requise, quel que soit le mode)
  const start = ref(todayIso());
  const end = ref(defaultEndIso());

  // Options avancées
  const calendarName = ref("");
  const cookie = ref("");
  const showAdvanced = ref(false);

  const resourceTypeLabel = computed(
    () => RESOURCE_TYPE_LABELS[resourceType.value],
  );

  const errors = computed(() => {
    const list: string[] = [];

    if (mode.value === "url") {
      if (!celcatUrl.value.trim()) list.push("Colle un lien Celcat.");
      else if (urlError.value) list.push(urlError.value);
    } else {
      if (!resourceId.value.trim())
        list.push(`Le champ « ${resourceTypeLabel.value} » est requis.`);
      if (!baseUrl.value.trim())
        list.push("L'URL de l'instance Celcat est requise.");
    }

    if (!start.value) list.push("La date de début est requise.");
    if (!end.value) list.push("La date de fin est requise.");
    if (start.value && end.value && end.value < start.value) {
      list.push(
        "La date de fin doit être postérieure ou égale à la date de début.",
      );
    }

    return list;
  });

  const canGenerate = computed(
    () =>
      errors.value.length === 0 &&
      !!resourceId.value.trim() &&
      !!baseUrl.value.trim(),
  );

  const attempted = ref(false);
  const generatedUrl = ref("");
  const copied = ref(false);

  function generate() {
    attempted.value = true;
    copied.value = false;

    if (!canGenerate.value) {
      generatedUrl.value = "";
      return;
    }

    const params = new URLSearchParams();
    params.set("resource_type", resourceType.value);
    params.set("resource_id", resourceId.value.trim());
    params.set("start", start.value);
    params.set("end", end.value);
    if (baseUrl.value.trim()) params.set("base_url", baseUrl.value.trim());
    if (calendarName.value.trim())
      params.set("calendar_name", calendarName.value.trim());
    if (cookie.value.trim()) params.set("cookie", cookie.value.trim());

    generatedUrl.value = `${apiBaseUrl.value}/calendar.ics?${params.toString()}`;
  }

  async function copyLink() {
    if (!generatedUrl.value) return;
    try {
      await navigator.clipboard.writeText(generatedUrl.value);
      copied.value = true;
      setTimeout(() => (copied.value = false), 2000);
    } catch {
      // Presse-papiers indisponible (contexte non sécurisé, permissions...) : on ignore.
    }
  }

  return {
    mode,
    celcatUrl,
    baseUrl,
    resourceType,
    resourceId,
    resourceTypeLabel,
    urlError,
    detected,
    start,
    end,
    calendarName,
    cookie,
    showAdvanced,
    errors,
    canGenerate,
    attempted,
    generatedUrl,
    copied,
    generate,
    copyLink,
  };
}
