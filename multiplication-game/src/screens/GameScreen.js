import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  View, Text, StyleSheet, SafeAreaView, Modal,
  TouchableOpacity, StatusBar,
} from 'react-native';
import { COLORS, DIFFICULTY, TOTAL_ROUNDS } from '../constants/theme';
import { generateQuestion, calcScore } from '../utils/gameLogic';
import PlayerPanel from '../components/PlayerPanel';

const FEEDBACK_DURATION = 1200;

function initPlayer(name) {
  return { name, score: 0, streak: 0, correct: 0, wrong: 0 };
}

export default function GameScreen({ route, navigation }) {
  const { name1, name2, difficulty } = route.params;
  const cfg = DIFFICULTY[difficulty];

  const [round, setRound] = useState(1);
  const [q1, setQ1] = useState(() => generateQuestion(difficulty));
  const [q2, setQ2] = useState(() => generateQuestion(difficulty));
  const [input1, setInput1] = useState('');
  const [input2, setInput2] = useState('');
  const [p1, setP1] = useState(() => initPlayer(name1));
  const [p2, setP2] = useState(() => initPlayer(name2));
  const [timeLeft, setTimeLeft] = useState(cfg.time);
  const [feedback1, setFeedback1] = useState(null);
  const [feedback2, setFeedback2] = useState(null);
  const [locked1, setLocked1] = useState(false);
  const [locked2, setLocked2] = useState(false);
  const [showRoundModal, setShowRoundModal] = useState(false);
  const [roundResult, setRoundResult] = useState(null);

  const timerRef = useRef(null);
  const timeRef = useRef(cfg.time);
  const roundRef = useRef(round);
  const locked1Ref = useRef(false);
  const locked2Ref = useRef(false);

  roundRef.current = round;

  const advanceRound = useCallback((forcedP1, forcedP2) => {
    const nextRound = roundRef.current + 1;
    const winner =
      forcedP1.score > forcedP2.score ? forcedP1.name :
      forcedP2.score > forcedP1.score ? forcedP2.name : 'Égalité';

    setRoundResult({ winner, p1: forcedP1, p2: forcedP2, round: roundRef.current });
    setShowRoundModal(true);

    if (nextRound > TOTAL_ROUNDS) {
      setTimeout(() => {
        setShowRoundModal(false);
        navigation.navigate('Result', { p1: forcedP1, p2: forcedP2, difficulty });
      }, 2000);
    } else {
      setTimeout(() => {
        setShowRoundModal(false);
        setRound(nextRound);
        setQ1(generateQuestion(difficulty));
        setQ2(generateQuestion(difficulty));
        setInput1('');
        setInput2('');
        setFeedback1(null);
        setFeedback2(null);
        locked1Ref.current = false;
        locked2Ref.current = false;
        setLocked1(false);
        setLocked2(false);
        timeRef.current = cfg.time;
        setTimeLeft(cfg.time);
      }, 1800);
    }
  }, [difficulty, navigation, cfg.time]);

  // Timer
  useEffect(() => {
    timerRef.current = setInterval(() => {
      timeRef.current -= 1;
      setTimeLeft(timeRef.current);

      if (timeRef.current <= 0) {
        clearInterval(timerRef.current);
        // Penalise unanswered
        setP1(prev => {
          const np = locked1Ref.current ? prev : { ...prev, wrong: prev.wrong + 1 };
          setP2(prev2 => {
            const np2 = locked2Ref.current ? prev2 : { ...prev2, wrong: prev2.wrong + 1 };
            advanceRound(np, np2);
            return np2;
          });
          return np;
        });
      }
    }, 1000);
    return () => clearInterval(timerRef.current);
  }, [round, advanceRound]);

  function handleKey(player, key) {
    const setInput = player === 1 ? setInput1 : setInput2;
    const setFeedback = player === 1 ? setFeedback1 : setFeedback2;
    const lockedRef = player === 1 ? locked1Ref : locked2Ref;
    const setLocked = player === 1 ? setLocked1 : setLocked2;
    const q = player === 1 ? q1 : q2;

    if (lockedRef.current) return;

    if (key === '⌫') {
      setInput(prev => prev.slice(0, -1));
      return;
    }

    if (key === '✓') {
      const val = player === 1 ? input1 : input2;
      submitAnswer(player, val, q, setFeedback, setLocked, lockedRef);
      return;
    }

    setInput(prev => {
      const next = prev + key;
      if (next.length >= 4) {
        submitAnswer(player, next, q, setFeedback, setLocked, lockedRef);
        return next;
      }
      return next;
    });
  }

  function submitAnswer(player, val, q, setFeedback, setLocked, lockedRef) {
    if (lockedRef.current) return;
    lockedRef.current = true;
    setLocked(true);

    const isCorrect = parseInt(val, 10) === q.answer;
    const fb = isCorrect ? 'correct' : 'wrong';
    setFeedback(fb);

    const pts = isCorrect ? calcScore(true, timeRef.current, cfg.time, cfg.points, 0) : 0;
    const setP = player === 1 ? setP1 : setP2;

    setP(prev => ({
      ...prev,
      score: prev.score + pts,
      streak: isCorrect ? prev.streak + 1 : 0,
      correct: isCorrect ? prev.correct + 1 : prev.correct,
      wrong: isCorrect ? prev.wrong : prev.wrong + 1,
    }));

    // Check if both answered
    setTimeout(() => {
      const otherLocked = player === 1 ? locked2Ref.current : locked1Ref.current;
      if (otherLocked) {
        clearInterval(timerRef.current);
        setP1(s1 => {
          setP2(s2 => {
            advanceRound(
              player === 1 ? { ...s1, score: s1.score + pts } : s1,
              player === 2 ? { ...s2, score: s2.score + pts } : s2,
            );
            return s2;
          });
          return s1;
        });
      }
    }, FEEDBACK_DURATION);
  }

  const roundWinner =
    roundResult
      ? roundResult.p1.score > roundResult.p2.score ? name1
        : roundResult.p2.score > roundResult.p1.score ? name2
        : 'Égalité'
      : '';

  return (
    <View style={styles.container}>
      <StatusBar hidden />

      {/* Player 1 top (rotated) */}
      <PlayerPanel
        playerName={p1.name}
        question={q1}
        input={input1}
        onKey={(k) => handleKey(1, k)}
        score={p1.score}
        streak={p1.streak}
        timeLeft={timeLeft}
        maxTime={cfg.time}
        isTop={true}
        feedback={feedback1}
        color={COLORS.player1}
        colorLight={COLORS.player1Light}
      />

      {/* Center Divider */}
      <View style={styles.divider}>
        <View style={styles.dividerLine} />
        <View style={styles.roundBadge}>
          <Text style={styles.roundText}>Round {round}/{TOTAL_ROUNDS}</Text>
          <Text style={styles.timerText}>{timeLeft}s</Text>
        </View>
        <View style={styles.dividerLine} />
      </View>

      {/* Player 2 bottom */}
      <PlayerPanel
        playerName={p2.name}
        question={q2}
        input={input2}
        onKey={(k) => handleKey(2, k)}
        score={p2.score}
        streak={p2.streak}
        timeLeft={timeLeft}
        maxTime={cfg.time}
        isTop={false}
        feedback={feedback2}
        color={COLORS.player2Light}
        colorLight={COLORS.player2Light}
      />

      {/* Round Result Modal */}
      <Modal visible={showRoundModal} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={styles.modalCard}>
            <Text style={styles.modalTitle}>Fin du round {round}</Text>
            <Text style={styles.modalWinner}>
              {roundWinner === 'Égalité' ? '🤝 Égalité !' : `🏆 ${roundWinner} mène !`}
            </Text>
            {roundResult && (
              <View style={styles.modalScores}>
                <Text style={[styles.modalScore, { color: COLORS.player1Light }]}>
                  {name1}: {roundResult.p1.score} pts
                </Text>
                <Text style={[styles.modalScore, { color: COLORS.player2Light }]}>
                  {name2}: {roundResult.p2.score} pts
                </Text>
              </View>
            )}
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  divider: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 8, paddingVertical: 4,
  },
  dividerLine: { flex: 1, height: 2, backgroundColor: 'rgba(255,255,255,0.3)' },
  roundBadge: {
    backgroundColor: 'rgba(255,255,255,0.12)', borderRadius: 20,
    paddingHorizontal: 16, paddingVertical: 4,
    alignItems: 'center', marginHorizontal: 8,
  },
  roundText: { color: COLORS.white, fontSize: 11, fontWeight: '700' },
  timerText: { color: COLORS.gold, fontSize: 14, fontWeight: '900' },
  modalOverlay: {
    flex: 1, backgroundColor: 'rgba(0,0,0,0.75)',
    justifyContent: 'center', alignItems: 'center',
  },
  modalCard: {
    backgroundColor: '#1e1e3a', borderRadius: 20,
    padding: 30, alignItems: 'center', width: '80%',
    borderWidth: 2, borderColor: COLORS.gold,
  },
  modalTitle: { color: COLORS.lightGray, fontSize: 14, marginBottom: 8 },
  modalWinner: { color: COLORS.gold, fontSize: 22, fontWeight: '900', textAlign: 'center' },
  modalScores: { marginTop: 16, gap: 4 },
  modalScore: { fontSize: 16, fontWeight: '700', textAlign: 'center' },
});
