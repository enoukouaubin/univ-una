import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity,
  StyleSheet, ScrollView, KeyboardAvoidingView, Platform,
} from 'react-native';
import { COLORS, DIFFICULTY } from '../constants/theme';

export default function WelcomeScreen({ navigation }) {
  const [name1, setName1] = useState('Joueur 1');
  const [name2, setName2] = useState('Joueur 2');
  const [difficulty, setDifficulty] = useState('medium');

  const startGame = () => {
    if (!name1.trim() || !name2.trim()) return;
    navigation.navigate('Game', { name1: name1.trim(), name2: name2.trim(), difficulty });
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.title}>✕ Tables de{'\n'}Multiplication</Text>
        <Text style={styles.subtitle}>Duel à 2 joueurs</Text>

        <View style={styles.card}>
          <Text style={styles.label}>Joueur 1 (haut)</Text>
          <TextInput
            style={[styles.input, { borderColor: COLORS.player1 }]}
            value={name1}
            onChangeText={setName1}
            maxLength={12}
            placeholder="Nom du joueur 1"
            placeholderTextColor="#666"
          />

          <Text style={styles.label}>Joueur 2 (bas)</Text>
          <TextInput
            style={[styles.input, { borderColor: COLORS.player2Light }]}
            value={name2}
            onChangeText={setName2}
            maxLength={12}
            placeholder="Nom du joueur 2"
            placeholderTextColor="#666"
          />
        </View>

        <View style={styles.card}>
          <Text style={styles.label}>Niveau de difficulté</Text>
          <View style={styles.diffRow}>
            {Object.entries(DIFFICULTY).map(([key, val]) => (
              <TouchableOpacity
                key={key}
                style={[styles.diffBtn, difficulty === key && styles.diffBtnActive]}
                onPress={() => setDifficulty(key)}
              >
                <Text style={[styles.diffText, difficulty === key && styles.diffTextActive]}>
                  {val.label}
                </Text>
                <Text style={[styles.diffSub, difficulty === key && styles.diffTextActive]}>
                  ×{val.max}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.rulesCard}>
          <Text style={styles.rulesTitle}>Comment jouer</Text>
          <Text style={styles.ruleText}>• Chaque joueur voit une multiplication</Text>
          <Text style={styles.ruleText}>• Tapez la bonne réponse le plus vite possible</Text>
          <Text style={styles.ruleText}>• Points bonus pour la vitesse et les séries</Text>
          <Text style={styles.ruleText}>• 10 manches — le score le plus haut gagne !</Text>
        </View>

        <TouchableOpacity style={styles.startBtn} onPress={startGame}>
          <Text style={styles.startText}>COMMENCER LE JEU</Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  scroll: { padding: 24, paddingTop: 60, alignItems: 'center' },
  title: {
    fontSize: 34, fontWeight: '900', color: COLORS.white,
    textAlign: 'center', lineHeight: 42,
  },
  subtitle: {
    fontSize: 16, color: COLORS.lightGray,
    marginTop: 8, marginBottom: 28, letterSpacing: 2,
  },
  card: {
    width: '100%', backgroundColor: 'rgba(255,255,255,0.07)',
    borderRadius: 16, padding: 20, marginBottom: 16,
  },
  label: { color: COLORS.lightGray, fontSize: 13, marginBottom: 8, letterSpacing: 1 },
  input: {
    borderWidth: 2, borderRadius: 10, padding: 12,
    color: COLORS.white, fontSize: 16, marginBottom: 16,
    backgroundColor: 'rgba(255,255,255,0.05)',
  },
  diffRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  diffBtn: {
    flex: 1, minWidth: '22%', paddingVertical: 10, paddingHorizontal: 6,
    borderRadius: 10, borderWidth: 2, borderColor: 'rgba(255,255,255,0.2)',
    alignItems: 'center',
  },
  diffBtnActive: { borderColor: COLORS.gold, backgroundColor: 'rgba(255,215,0,0.15)' },
  diffText: { color: COLORS.lightGray, fontSize: 12, fontWeight: '600' },
  diffSub: { color: '#888', fontSize: 11, marginTop: 2 },
  diffTextActive: { color: COLORS.gold },
  rulesCard: {
    width: '100%', backgroundColor: 'rgba(255,255,255,0.04)',
    borderRadius: 16, padding: 20, marginBottom: 16,
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)',
  },
  rulesTitle: { color: COLORS.gold, fontWeight: '700', marginBottom: 10, fontSize: 14 },
  ruleText: { color: COLORS.lightGray, fontSize: 13, marginBottom: 5 },
  startBtn: {
    width: '100%', backgroundColor: COLORS.player1,
    borderRadius: 16, padding: 18, alignItems: 'center', marginTop: 8,
  },
  startText: { color: COLORS.white, fontWeight: '900', fontSize: 18, letterSpacing: 2 },
});
