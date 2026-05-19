# Tables de Multiplication — Duel 2 Joueurs

Application mobile React Native (Expo) pour jouer aux tables de multiplication à deux.

## Installation rapide

### Prérequis
- Node.js 18+ installé sur votre PC
- Application **Expo Go** sur votre téléphone (disponible sur Play Store / App Store)
- PC et téléphone sur le **même réseau WiFi**

### Étapes

```bash
# 1. Aller dans le dossier
cd multiplication-game

# 2. Installer les dépendances
npm install

# 3. Lancer le serveur
npx expo start
```

Un **QR code** s'affiche dans le terminal.  
Scannez-le avec l'application **Expo Go** sur votre téléphone.

---

## Comment jouer

1. Entrez les noms des deux joueurs
2. Choisissez la difficulté (Facile → Expert)
3. Posez le téléphone à plat entre les deux joueurs
4. **Joueur 1** utilise la moitié du haut (écran retourné)
5. **Joueur 2** utilise la moitié du bas
6. Chaque joueur voit sa propre multiplication
7. Tapez la réponse et appuyez sur **✓** pour valider
8. 10 manches — le score le plus haut gagne !

## Système de points

| Action | Points |
|--------|--------|
| Bonne réponse | 10–30 pts selon difficulté |
| Bonus de vitesse | jusqu'à +5 pts |
| Série de 3+ bonnes réponses | +5 pts bonus |
| Mauvaise réponse | 0 pt |

## Niveaux de difficulté

| Niveau | Nombres | Temps |
|--------|---------|-------|
| Facile | 1–5 | 15s |
| Moyen | 1–10 | 12s |
| Difficile | 1–12 | 10s |
| Expert | 5–20 | 8s |
