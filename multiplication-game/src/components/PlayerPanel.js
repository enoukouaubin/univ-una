import React, { useEffect, useRef } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, Animated,
} from 'react-native';
import { COLORS } from '../constants/theme';

const KEYS = [
  ['1','2','3'],
  ['4','5','6'],
  ['7','8','9'],
  ['⌫','0','✓'],
];

export default function PlayerPanel({
  playerName, question, input, onKey,
  score, streak, timeLeft, maxTime, isTop,
  feedback, color, colorLight,
}) {
  const shakeAnim = useRef(new Animated.Value(0)).current;
  const flashAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (feedback === 'wrong') {
      Animated.sequence([
        Animated.timing(shakeAnim, { toValue: 8, duration: 60, useNativeDriver: true }),
        Animated.timing(shakeAnim, { toValue: -8, duration: 60, useNativeDriver: true }),
        Animated.timing(shakeAnim, { toValue: 6, duration: 60, useNativeDriver: true }),
        Animated.timing(shakeAnim, { toValue: 0, duration: 60, useNativeDriver: true }),
      ]).start();
    }
    if (feedback === 'correct') {
      Animated.sequence([
        Animated.timing(flashAnim, { toValue: 1, duration: 150, useNativeDriver: false }),
        Animated.timing(flashAnim, { toValue: 0, duration: 300, useNativeDriver: false }),
      ]).start();
    }
  }, [feedback]);

  const flashBg = flashAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['transparent', 'rgba(76,175,80,0.3)'],
  });

  const timerPct = timeLeft / maxTime;
  const timerColor = timerPct > 0.5 ? COLORS.correct : timerPct > 0.25 ? COLORS.gold : COLORS.wrong;

  const content = (
    <Animated.View
      style={[styles.panel, { backgroundColor: flashBg, transform: [{ translateX: shakeAnim }] }]}
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={[styles.name, { color: colorLight }]}>{playerName}</Text>
        <View style={styles.scoreRow}>
          <Text style={[styles.score, { color: colorLight }]}>{score} pts</Text>
          {streak >= 2 && (
            <Text style={styles.streak}>🔥 ×{streak}</Text>
          )}
        </View>
      </View>

      {/* Timer bar */}
      <View style={styles.timerBg}>
        <View style={[styles.timerFill, { width: `${timerPct * 100}%`, backgroundColor: timerColor }]} />
      </View>

      {/* Question */}
      <Animated.View style={[styles.questionBox, { borderColor: color }]}>
        <Text style={styles.questionText}>
          {question.a} × {question.b} = ?
        </Text>
        <Text style={[styles.inputText, { color: colorLight }]}>
          {input || '...'}
        </Text>
        {feedback === 'correct' && (
          <Text style={styles.feedbackCorrect}>✓ +{score}</Text>
        )}
        {feedback === 'wrong' && (
          <Text style={styles.feedbackWrong}>✗ {question.a * question.b}</Text>
        )}
      </Animated.View>

      {/* Numpad */}
      <View style={styles.numpad}>
        {KEYS.map((row, ri) => (
          <View key={ri} style={styles.row}>
            {row.map((k) => (
              <TouchableOpacity
                key={k}
                style={[
                  styles.key,
                  k === '✓' && styles.keyConfirm,
                  k === '⌫' && styles.keyDel,
                ]}
                onPress={() => onKey(k)}
                activeOpacity={0.6}
              >
                <Text style={[
                  styles.keyText,
                  k === '✓' && styles.keyConfirmText,
                ]}>
                  {k}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        ))}
      </View>
    </Animated.View>
  );

  return isTop ? (
    <View style={[styles.rotated, { flex: 1 }]}>
      {content}
    </View>
  ) : (
    <View style={{ flex: 1 }}>
      {content}
    </View>
  );
}

const styles = StyleSheet.create({
  rotated: { transform: [{ rotate: '180deg' }] },
  panel: { flex: 1, padding: 10, justifyContent: 'space-between' },
  header: {
    flexDirection: 'row', justifyContent: 'space-between',
    alignItems: 'center', paddingHorizontal: 4,
  },
  name: { fontWeight: '800', fontSize: 15 },
  scoreRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  score: { fontWeight: '700', fontSize: 15 },
  streak: { fontSize: 13 },
  timerBg: {
    height: 5, backgroundColor: 'rgba(255,255,255,0.15)',
    borderRadius: 3, marginVertical: 6,
  },
  timerFill: { height: 5, borderRadius: 3 },
  questionBox: {
    borderWidth: 2, borderRadius: 14, padding: 12,
    alignItems: 'center', backgroundColor: 'rgba(255,255,255,0.05)',
  },
  questionText: { color: '#fff', fontSize: 22, fontWeight: '700' },
  inputText: { fontSize: 28, fontWeight: '900', marginTop: 4 },
  feedbackCorrect: { color: COLORS.correct, fontWeight: '700', fontSize: 14, marginTop: 4 },
  feedbackWrong: { color: COLORS.wrong, fontWeight: '700', fontSize: 14, marginTop: 4 },
  numpad: { gap: 6 },
  row: { flexDirection: 'row', gap: 6 },
  key: {
    flex: 1, paddingVertical: 12, borderRadius: 10,
    backgroundColor: COLORS.keyBg, alignItems: 'center',
  },
  keyConfirm: { backgroundColor: COLORS.correct },
  keyDel: { backgroundColor: 'rgba(244,67,54,0.3)' },
  keyText: { color: '#fff', fontSize: 20, fontWeight: '700' },
  keyConfirmText: { color: '#fff' },
});
