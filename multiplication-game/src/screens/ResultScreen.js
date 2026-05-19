import React from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView,
} from 'react-native';
import { COLORS } from '../constants/theme';
import { getRankTitle } from '../utils/gameLogic';

export default function ResultScreen({ route, navigation }) {
  const { p1, p2, difficulty } = route.params;

  const p1Wins = p1.score > p2.score;
  const draw = p1.score === p2.score;
  const winner = draw ? null : p1Wins ? p1 : p2;
  const loser = draw ? null : p1Wins ? p2 : p1;

  const accuracy1 = p1.correct + p1.wrong > 0
    ? Math.round((p1.correct / (p1.correct + p1.wrong)) * 100) : 0;
  const accuracy2 = p2.correct + p2.wrong > 0
    ? Math.round((p2.correct / (p2.correct + p2.wrong)) * 100) : 0;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Résultats Finaux</Text>

      {draw ? (
        <View style={styles.drawBanner}>
          <Text style={styles.drawText}>🤝 ÉGALITÉ !</Text>
        </View>
      ) : (
        <View style={styles.winnerBanner}>
          <Text style={styles.crown}>👑</Text>
          <Text style={styles.winnerName}>{winner.name}</Text>
          <Text style={styles.winnerSub}>GAGNANT !</Text>
          <Text style={styles.rank}>{getRankTitle(winner.score)}</Text>
        </View>
      )}

      <View style={styles.scoreRow}>
        <PlayerCard
          player={p1}
          accuracy={accuracy1}
          color={COLORS.player1}
          colorLight={COLORS.player1Light}
          isWinner={!draw && p1Wins}
        />
        <View style={styles.vsBox}>
          <Text style={styles.vs}>VS</Text>
        </View>
        <PlayerCard
          player={p2}
          accuracy={accuracy2}
          color={COLORS.player2Light}
          colorLight={COLORS.player2Light}
          isWinner={!draw && !p1Wins}
        />
      </View>

      {!draw && (
        <View style={styles.marginCard}>
          <Text style={styles.marginText}>
            Écart de victoire:{' '}
            <Text style={{ color: COLORS.gold, fontWeight: '900' }}>
              {Math.abs(p1.score - p2.score)} points
            </Text>
          </Text>
        </View>
      )}

      <TouchableOpacity
        style={styles.replayBtn}
        onPress={() => navigation.navigate('Game', route.params)}
      >
        <Text style={styles.replayText}>▶ REJOUER</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.homeBtn}
        onPress={() => navigation.navigate('Welcome')}
      >
        <Text style={styles.homeText}>Accueil</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

function PlayerCard({ player, accuracy, color, colorLight, isWinner }) {
  return (
    <View style={[styles.playerCard, isWinner && { borderColor: COLORS.gold }]}>
      {isWinner && <Text style={styles.winTag}>GAGNANT</Text>}
      <Text style={[styles.cardName, { color: colorLight }]}>{player.name}</Text>
      <Text style={[styles.cardScore, { color: colorLight }]}>{player.score}</Text>
      <Text style={styles.cardScoreLabel}>points</Text>
      <View style={styles.statsBox}>
        <Stat label="✓ Corrects" value={player.correct} />
        <Stat label="✗ Faux" value={player.wrong} />
        <Stat label="Précision" value={`${accuracy}%`} />
      </View>
    </View>
  );
}

function Stat({ label, value }) {
  return (
    <View style={styles.stat}>
      <Text style={styles.statVal}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  content: { padding: 20, paddingTop: 60, alignItems: 'center' },
  title: {
    color: COLORS.white, fontSize: 26, fontWeight: '900',
    marginBottom: 20, letterSpacing: 1,
  },
  drawBanner: {
    backgroundColor: 'rgba(255,215,0,0.15)', borderRadius: 20,
    padding: 20, marginBottom: 20, borderWidth: 2, borderColor: COLORS.gold,
  },
  drawText: { color: COLORS.gold, fontSize: 28, fontWeight: '900' },
  winnerBanner: {
    backgroundColor: 'rgba(255,215,0,0.1)', borderRadius: 20,
    padding: 20, marginBottom: 20, alignItems: 'center',
    borderWidth: 2, borderColor: COLORS.gold, width: '100%',
  },
  crown: { fontSize: 40 },
  winnerName: { color: COLORS.gold, fontSize: 28, fontWeight: '900', marginTop: 4 },
  winnerSub: { color: COLORS.lightGray, fontSize: 13, letterSpacing: 3 },
  rank: { color: COLORS.gold, fontSize: 16, marginTop: 6, fontWeight: '600' },
  scoreRow: {
    flexDirection: 'row', width: '100%',
    alignItems: 'stretch', marginBottom: 16, gap: 8,
  },
  vsBox: { justifyContent: 'center', alignItems: 'center', width: 30 },
  vs: { color: '#666', fontWeight: '900', fontSize: 14 },
  playerCard: {
    flex: 1, backgroundColor: 'rgba(255,255,255,0.06)',
    borderRadius: 16, padding: 14, alignItems: 'center',
    borderWidth: 2, borderColor: 'rgba(255,255,255,0.1)',
  },
  winTag: {
    color: COLORS.gold, fontSize: 9, fontWeight: '900',
    letterSpacing: 1, marginBottom: 4,
  },
  cardName: { fontSize: 15, fontWeight: '800', textAlign: 'center' },
  cardScore: { fontSize: 36, fontWeight: '900', marginTop: 4 },
  cardScoreLabel: { color: '#888', fontSize: 11 },
  statsBox: { marginTop: 10, gap: 6, width: '100%' },
  stat: { alignItems: 'center' },
  statVal: { color: COLORS.white, fontWeight: '700', fontSize: 16 },
  statLabel: { color: '#888', fontSize: 10 },
  marginCard: {
    backgroundColor: 'rgba(255,255,255,0.06)', borderRadius: 12,
    padding: 14, marginBottom: 16, width: '100%', alignItems: 'center',
  },
  marginText: { color: COLORS.lightGray, fontSize: 14 },
  replayBtn: {
    width: '100%', backgroundColor: COLORS.player1,
    borderRadius: 14, padding: 16, alignItems: 'center', marginBottom: 10,
  },
  replayText: { color: COLORS.white, fontWeight: '900', fontSize: 16, letterSpacing: 2 },
  homeBtn: {
    width: '100%', borderWidth: 2, borderColor: 'rgba(255,255,255,0.2)',
    borderRadius: 14, padding: 14, alignItems: 'center', marginBottom: 30,
  },
  homeText: { color: COLORS.lightGray, fontWeight: '700', fontSize: 14 },
});
