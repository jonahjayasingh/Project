import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  StatusBar,
  Alert,
  Animated,
  Dimensions,
  Platform
} from 'react-native';

const { width } = Dimensions.get('window');
const QUEUE_WIDTH = 120;
const BOX_HEIGHT = 60;
const BOX_MARGIN = 8;

export const QueueVisualizer = () => {
  const [queue, setQueue] = useState<number[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [operation, setOperation] = useState<string | null>(null);
  const [status, setStatus] = useState('Queue is empty. Enqueue some values!');
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const animation = useRef(new Animated.Value(0)).current;

  const enqueue = () => {
    const num = parseInt(inputValue);
    if (isNaN(num)) {
      Alert.alert('Invalid input', 'Please enter a valid number');
      return;
    }

    const newQueue = [...queue, num];
    setQueue(newQueue);
    setOperation('enqueue');
    setStatus(`Enqueued ${num} to the rear`);
    setSelectedIndex(newQueue.length - 1);
    setInputValue('');
    animateOperation();
  };

  const dequeue = () => {
    if (queue.length === 0) {
      setStatus('Queue is empty. Cannot dequeue.');
      return;
    }

    const dequeuedValue = queue[0];
    const newQueue = queue.slice(1);
    setQueue(newQueue);
    setOperation('dequeue');
    setStatus(`Dequeued ${dequeuedValue} from the front`);
    setSelectedIndex(null);
    animateOperation();
  };

  const front = () => {
    if (queue.length === 0) {
      setStatus('Queue is empty.');
      return;
    }

    const frontValue = queue[0];
    setOperation('front');
    setStatus(`Front element is ${frontValue}`);
    setSelectedIndex(0);
    animateOperation(true); // Quick animation for front
  };

  const clear = () => {
    if (queue.length === 0) {
      setStatus('Queue is already empty');
      return;
    }

    setQueue([]);
    setOperation('clear');
    setStatus('Queue cleared');
    setSelectedIndex(null);
  };

  const animateOperation = (quick = false) => {
    setIsAnimating(true);
    animation.setValue(0);
    Animated.timing(animation, {
      toValue: 1,
      duration: quick ? 300 : 600,
      useNativeDriver: true,
    }).start(() => setIsAnimating(false));
  };

  const renderQueueItem = (value: number, index: number, isFront: boolean, isRear: boolean) => {
    const isSelected = selectedIndex === index;

    return (
      <Animated.View
        key={index}
        style={[
          styles.queueItem,
          isFront && styles.frontItem,
          isRear && styles.rearItem,
          isSelected && styles.selectedItem,
          {
            transform: [
              {
                translateX: animation.interpolate({
                  inputRange: [0, 1],
                  outputRange: [isSelected && operation === 'enqueue' ? 50 : 0, 0]
                })
              },
              {
                scale: isSelected
                  ? animation.interpolate({
                      inputRange: [0, 0.5, 1],
                      outputRange: [1, 1.2, 1.1]
                    })
                  : 1
              }
            ],
            marginLeft: index === 0 ? 0 : -20, // Overlap effect for horizontal queue
          }
        ]}
      >
        <Text style={styles.itemValue}>{value}</Text>
        {isFront && <Text style={styles.frontLabel}>FRONT</Text>}
        {isRear && <Text style={styles.rearLabel}>REAR</Text>}
        <Text style={styles.indexLabel}>[{index}]</Text>
      </Animated.View>
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.header}>📥 Queue Visualizer</Text>
        <Text style={styles.subtitle}>FIFO (First-In-First-Out) Data Structure</Text>

        <View style={styles.statsContainer}>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Queue Size</Text>
            <Text style={styles.statValue}>{queue.length}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Capacity</Text>
            <Text style={styles.statValue}>∞</Text>
          </View>
        </View>

        <View style={styles.inputSection}>
          <Text style={styles.sectionTitle}>Queue Operations</Text>
          
          <TextInput
            style={styles.input}
            placeholder="Enter value to enqueue"
            value={inputValue}
            onChangeText={setInputValue}
            keyboardType="numeric"
            onSubmitEditing={enqueue}
          />

          <View style={styles.buttonGrid}>
            <TouchableOpacity 
              style={[styles.operationButton, styles.enqueueButton]}
              onPress={enqueue}
              disabled={isAnimating}
            >
              <Text style={styles.buttonText}>Enqueue</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.operationButton, styles.dequeueButton]}
              onPress={dequeue}
              disabled={isAnimating || queue.length === 0}
            >
              <Text style={styles.buttonText}>Dequeue</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.operationButton, styles.frontButton]}
              onPress={front}
              disabled={isAnimating || queue.length === 0}
            >
              <Text style={styles.buttonText}>Front</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.operationButton, styles.clearButton]}
              onPress={clear}
              disabled={isAnimating || queue.length === 0}
            >
              <Text style={styles.buttonText}>Clear</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.statusContainer}>
          <Text style={styles.status}>{status}</Text>
          {operation && (
            <Text style={styles.operationText}>
              Last operation: {operation.toUpperCase()}
            </Text>
          )}
        </View>

        <View style={styles.visualizationSection}>
          <Text style={styles.sectionTitle}>Queue Visualization</Text>
          
          {queue.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={styles.emptyText}>📭 Queue is empty</Text>
              <Text style={styles.emptySubtext}>Enqueue some values to get started</Text>
            </View>
          ) : (
            <View style={styles.queueContainer}>
              <View style={styles.queue}>
                {queue.map((value, index) => 
                  renderQueueItem(value, index, index === 0, index === queue.length - 1)
                )}
              </View>
              
              <View style={styles.queueDirection}>
                <Text style={styles.directionText}>→ Processing Direction →</Text>
              </View>
            </View>
          )}
        </View>

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>📖 About Queue:</Text>
          <Text style={styles.infoText}>
            • FIFO (First-In-First-Out) structure{'\n'}
            • Operations: Enqueue (add to rear), Dequeue (remove from front){'\n'}
            • Time Complexity: O(1) for all operations{'\n'}
            • Used in: Task scheduling, breadth-first search, buffering{'\n'}
            • Real-world examples: Waiting lines, printer queues, message queues
          </Text>
        </View>

        <View style={styles.legendCard}>
          <Text style={styles.legendTitle}>Legend:</Text>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.frontItem]} />
            <Text style={styles.legendText}>Front element (next to be dequeued)</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.rearItem]} />
            <Text style={styles.legendText}>Rear element (most recently enqueued)</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.selectedItem]} />
            <Text style={styles.legendText}>Selected element (recent operation)</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.queueItem]} />
            <Text style={styles.legendText}>Regular queue element</Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const PRIMARY_COLOR = '#2563eb';
const ENQUEUE_COLOR = '#10b981';
const DEQUEUE_COLOR = '#ef4444';
const FRONT_COLOR = '#f59e0b';
const LIGHT_BG = '#f9fafb';

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: LIGHT_BG,
    paddingTop: StatusBar.currentHeight,
  },
  container: {
    flexGrow: 1,
    padding: 24,
    paddingBottom: 40,
  },
  header: {
    fontSize: 32,
    fontWeight: '800',
    color: PRIMARY_COLOR,
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    marginBottom: 32,
    textAlign: 'center',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 24,
  },
  statBox: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    minWidth: 100,
    borderWidth: 2,
    borderColor: '#e5e7eb',
  },
  statLabel: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 20,
    fontWeight: '700',
    color: PRIMARY_COLOR,
  },
  inputSection: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: PRIMARY_COLOR,
    marginBottom: 16,
  },
  input: {
    height: 50,
    borderWidth: 2,
    borderColor: '#e5e7eb',
    borderRadius: 12,
    paddingHorizontal: 16,
    fontSize: 16,
    backgroundColor: 'white',
    marginBottom: 16,
    color: '#1f2937',
  },
  buttonGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-evenly',
    gap: 12,
    ...(Platform.OS === "web" &&{
      display:'flex'
    })  
  },
  operationButton: {
    width: Platform.OS === "web" ? "20%" :'48%',
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  enqueueButton: {
    backgroundColor: ENQUEUE_COLOR,
  },
  dequeueButton: {
    backgroundColor: DEQUEUE_COLOR,
  },
  frontButton: {
    backgroundColor: FRONT_COLOR,
  },
  clearButton: {
    backgroundColor: '#6b7280',
  },
  buttonText: {
    color: 'white',
    fontWeight: '700',
    fontSize: 14,
    textAlign: 'center',
  },
  statusContainer: {
    backgroundColor: '#e0e7ff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 24,
    borderLeftWidth: 4,
    borderLeftColor: PRIMARY_COLOR,
  },
  status: {
    fontSize: 16,
    fontWeight: '600',
    color: PRIMARY_COLOR,
    textAlign: 'center',
    marginBottom: 8,
  },
  operationText: {
    fontSize: 14,
    color: '#6366f1',
    textAlign: 'center',
    fontStyle: 'italic',
  },
  visualizationSection: {
    marginBottom: 24,
  },
  queueContainer: {
    alignItems: 'center',
  },
  queue: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
    minHeight: 100,
  },
  queueItem: {
    width: QUEUE_WIDTH,
    height: BOX_HEIGHT,
    backgroundColor: PRIMARY_COLOR,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: BOX_MARGIN / 2,
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 4 },
    position: 'relative',
  },
  frontItem: {
    backgroundColor: DEQUEUE_COLOR,
    borderWidth: 3,
    borderColor: '#dc2626',
  },
  rearItem: {
    backgroundColor: ENQUEUE_COLOR,
    borderWidth: 3,
    borderColor: '#059669',
  },
  selectedItem: {
    backgroundColor: FRONT_COLOR,
    borderWidth: 3,
    borderColor: '#d97706',
  },
  itemValue: {
    fontSize: 20,
    fontWeight: '800',
    color: 'white',
  },
  frontLabel: {
    position: 'absolute',
    top: 4,
    left: 8,
    fontSize: 12,
    fontWeight: '700',
    color: 'white',
    backgroundColor: 'rgba(0,0,0,0.3)',
    paddingHorizontal: 6,
    borderRadius: 8,
  },
  rearLabel: {
    position: 'absolute',
    top: 4,
    right: 8,
    fontSize: 12,
    fontWeight: '700',
    color: 'white',
    backgroundColor: 'rgba(0,0,0,0.3)',
    paddingHorizontal: 6,
    borderRadius: 8,
  },
  indexLabel: {
    position: 'absolute',
    bottom: 4,
    left: 8,
    fontSize: 12,
    color: 'rgba(255,255,255,0.8)',
  },
  queueDirection: {
    marginTop: 10,
    padding: 8,
    backgroundColor: '#f3f4f6',
    borderRadius: 8,
  },
  directionText: {
    fontSize: 14,
    color: '#6b7280',
    fontWeight: '600',
  },
  emptyState: {
    padding: 40,
    alignItems: 'center',
    backgroundColor: 'white',
    borderRadius: 16,
    borderWidth: 2,
    borderColor: '#e5e7eb',
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#6b7280',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#9ca3af',
  },
  infoCard: {
    backgroundColor: '#f0f9ff',
    padding: 20,
    borderRadius: 16,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: PRIMARY_COLOR,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: PRIMARY_COLOR,
    marginBottom: 12,
  },
  infoText: {
    fontSize: 14,
    lineHeight: 20,
    color: '#374151',
  },
  legendCard: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: '#e5e7eb',
  },
  legendTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: PRIMARY_COLOR,
    marginBottom: 12,
    textAlign: 'center',
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  legendColor: {
    width: 20,
    height: 20,
    borderRadius: 6,
    marginRight: 12,
    borderWidth: 2,
  },
  legendText: {
    fontSize: 14,
    color: '#374151',
    fontWeight: '500',
  },
});