const SITE_NAME = 'Celcat → ICS'
const SITE_TITLE = 'Celcat → ICS — Ton emploi du temps, enfin lisible'
const SITE_DESCRIPTION =
  "Génère en quelques secondes un lien de calendrier (ICS) à partir de ton emploi du temps Celcat. Compatible Google Calendar, Apple Calendar, Outlook. Projet étudiant, non officiel."

/**
 * Métadonnées SEO + partage social (Open Graph, Twitter Card, JSON-LD).
 *
 * L'URL du site est déduite automatiquement de la requête entrante
 * (`useRequestURL`), sauf si `NUXT_PUBLIC_SITE_URL` est explicitement
 * configurée — pratique tant que le nom de domaine final n'est pas figé.
 */
export function useSiteSeo() {
  const config = useRuntimeConfig()
  const requestUrl = useRequestURL()

  const siteUrl = computed(() => {
    const configured = config.public.siteUrl ? String(config.public.siteUrl) : ''
    const base = configured || `${requestUrl.protocol}//${requestUrl.host}`
    return base.replace(/\/$/, '')
  })

  const ogImageUrl = computed(() => `${siteUrl.value}/og-image.png`)

  useSeoMeta({
    title: SITE_TITLE,
    description: SITE_DESCRIPTION,
    robots: 'index, follow',
    ogType: 'website',
    ogSiteName: SITE_NAME,
    ogTitle: SITE_TITLE,
    ogDescription: SITE_DESCRIPTION,
    ogUrl: siteUrl,
    ogImage: ogImageUrl,
    ogImageWidth: 1200,
    ogImageHeight: 630,
    ogImageAlt: SITE_TITLE,
    ogLocale: 'fr_FR',
    twitterCard: 'summary_large_image',
    twitterTitle: SITE_TITLE,
    twitterDescription: SITE_DESCRIPTION,
    twitterImage: ogImageUrl
  })

  useHead({
    link: [{ rel: 'canonical', href: siteUrl }],
    script: [
      {
        type: 'application/ld+json',
        innerHTML: computed(() =>
          JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'WebApplication',
            name: SITE_NAME,
            url: siteUrl.value,
            description: SITE_DESCRIPTION,
            applicationCategory: 'UtilitiesApplication',
            operatingSystem: 'Any (web)',
            offers: { '@type': 'Offer', price: '0', priceCurrency: 'EUR' },
            creator: { '@type': 'Organization', name: 'Projet étudiant indépendant' }
          })
        )
      }
    ]
  })

  return { siteUrl, ogImageUrl }
}
