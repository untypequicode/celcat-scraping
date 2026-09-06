export type ColorScheme = 'light' | 'dark'

const STORAGE_KEY = 'color-scheme'

/**
 * Détection + bascule du thème clair/sombre.
 *
 * Au premier appel côté client, suit la préférence système
 * (`prefers-color-scheme`) tant que l'utilisateur n'a pas fait de choix
 * manuel (persisté en localStorage). Le flash visuel au chargement est
 * évité par un script bloquant injecté dans `nuxt.config.ts`.
 */
export function useColorScheme() {
  const scheme = useState<ColorScheme>('color-scheme', () => 'light')

  function applyToDocument(value: ColorScheme) {
    if (!import.meta.client) return
    document.documentElement.classList.toggle('dark', value === 'dark')
  }

  function set(value: ColorScheme, persist = true) {
    scheme.value = value
    applyToDocument(value)
    if (persist && import.meta.client) {
      localStorage.setItem(STORAGE_KEY, value)
    }
  }

  function init() {
    if (!import.meta.client) return

    const stored = localStorage.getItem(STORAGE_KEY) as ColorScheme | null
    const media = window.matchMedia('(prefers-color-scheme: dark)')

    scheme.value = stored ?? (media.matches ? 'dark' : 'light')
    applyToDocument(scheme.value)

    // Si l'utilisateur n'a jamais choisi manuellement, on continue de
    // suivre les changements de préférence système en temps réel.
    media.addEventListener('change', (event) => {
      if (!localStorage.getItem(STORAGE_KEY)) {
        set(event.matches ? 'dark' : 'light', false)
      }
    })
  }

  function toggle() {
    set(scheme.value === 'dark' ? 'light' : 'dark')
  }

  return { scheme, init, toggle, set }
}
