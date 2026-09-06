// Initialise le thème clair/sombre au tout début du cycle de vie client
// (avant le montage de l'app), pour que le petit interrupteur de thème
// affiche immédiatement le bon état, sans flicker au premier rendu.
export default defineNuxtPlugin(() => {
  const { init } = useColorScheme()
  init()
})
