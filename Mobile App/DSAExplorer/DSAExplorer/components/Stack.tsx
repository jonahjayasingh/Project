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
const STACK_WIDTH = 120;
const BOX_HEIGHT = 60;
const BOX_MARGIN = 8;

export const StackVisualizer = () => {
  const [stack, setStack] = useState<number[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [operation, setOperation] = useState<string | null>(null);
  const [status, setStatus] = useState('Stack is empty. Push some values!');
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const animation = useRef(new Animated.Value(0)).current;

  const push = () => {
    const num = parseInt(inputValue);
    if (isNaN(num)) {
      Alert.alert('Invalid input', 'Please enter a valid number');
      return;
    }

    const newStack = [...stack, num];
    setStack(newStack);
    setOperation('push');
    setStatus(`Pushed ${num} onto the stack`);
    setSelectedIndex(newStack.length - 1);
    setInputValue('');
    animateOperation();
  };

  const pop = () => {
    if (stack.length === 0) {
      setStatus('Stack is empty. Cannot pop.');
      return;
    }

    const poppedValue = stack[stack.length - 1];
    const newStack = stack.slice(0, -1);
    setStack(newStack);
    setOperation('pop');
    setStatus(`Popped ${poppedValue} from the stack`);
    setSelectedIndex(null);
    animateOperation();
  };

  const peek = () => {
    if (stack.length === 0) {
      setStatus('Stack is empty.');
      return;
    }

    const topValue = stack[stack.length - 1];
    setOperation('peek');
    setStatus(`Top element is ${topValue}`);
    setSelectedIndex(stack.length - 1);
    animateOperation(true); // Quick animation for peek
  };

  const clear = () => {
    if (stack.length === 0) {
      setStatus('Stack is already empty');
      return;
    }

    setStack([]);
    setOperation('clear');
    setStatus('Stack cleared');
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

  const renderStackItem = (value: number, index: number, isTop: boolean) => {
    const isSelected = selectedIndex === index;
    const positionFromTop = stack.length - 1 - index;

    return (
      <Animated.View
        key={index}
        style={[
          styles.stackItem,
          isTop && styles.topItem,
          isSelected && styles.selectedItem,
          {
            transform: [
              {
                translateY: animation.interpolate({
                  inputRange: [0, 1],
                  outputRange: [isSelected && operation === 'push' ? -50 : 0, 0]
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
            zIndex: stack.length - index,
            marginBottom: 4, // Fixed: Changed from marginTop to marginBottom to prevent overlapping
          }
        ]}
      >
        <Text style={styles.itemValue}>{value}</Text>
        {isTop && <Text style={styles.topLabel}>TOP</Text>}
        <Text style={styles.indexLabel}>[{index}]</Text>
      </Animated.View>
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.header}>🗂 Stack Visualizer</Text>
        <Text style={styles.subtitle}>LIFO (Last-In-First-Out) Data Structure</Text>

        <View style={styles.statsContainer}>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Stack Size</Text>
            <Text style={styles.statValue}>{stack.length}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Capacity</Text>
            <Text style={styles.statValue}>∞</Text>
          </View>
        </View>

        <View style={styles.inputSection}>
          <Text style={styles.sectionTitle}>Stack Operations</Text>
          
          <TextInput
            style={styles.input}
            placeholder="Enter value to push"
            value={inputValue}
            onChangeText={setInputValue}
            keyboardType="numeric"
            onSubmitEditing={push}
          />

          <View style={styles.buttonGrid}>
            <TouchableOpacity 
              style={[styles.operationButton, styles.pushButton]}
              onPress={push}
              disabled={isAnimating}
            >
              <Text style={styles.buttonText}>Push</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.operationButton, styles.popButton]}
              onPress={pop}
              disabled={isAnimating || stack.length === 0}
            >
              <Text style={styles.buttonText}>Pop</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.operationButton, styles.peekButton]}
              onPress={peek}
              disabled={isAnimating || stack.length === 0}
            >
              <Text style={styles.buttonText}>Peek</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.operationButton, styles.clearButton]}
              onPress={clear}
              disabled={isAnimating || stack.length === 0}
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
          <Text style={styles.sectionTitle}>Stack Visualization</Text>
          
          {stack.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={styles.emptyText}>📭 Stack is empty</Text>
              <Text style={styles.emptySubtext}>Push some values to get started</Text>
            </View>
          ) : (
            <View style={styles.stackContainer}>
              <View style={styles.stack}>
                {stack.map((value, index) => 
                  renderStackItem(value, index, index === stack.length - 1)
                )}
              </View>
              
              <View style={styles.stackBase}>
                <Text style={styles.baseText}>Stack Base</Text>
              </View>
            </View>
          )}
        </View>

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>📖 About Stack:</Text>
          <Text style={styles.infoText}>
            • LIFO (Last-In-First-Out) structure{'\n'}
            • Operations: Push (add), Pop (remove), Peek (view top){'\n'}
            • Time Complexity: O(1) for all operations{'\n'}
            • Used in: Function calls, undo/redo, expression evaluation{'\n'}
            • Real-world examples: Stack of plates, browser back button
          </Text>
        </View>

        <View style={styles.legendCard}>
          <Text style={styles.legendTitle}>Legend:</Text>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.topItem]} />
            <Text style={styles.legendText}>Top element (next to be popped)</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.selectedItem]} />
            <Text style={styles.legendText}>Selected element (recent operation)</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.stackItem]} />
            <Text style={styles.legendText}>Regular stack element</Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const PRIMARY_COLOR = '#2563eb';
const PUSH_COLOR = '#10b981';
const POP_COLOR = '#ef4444';
const PEEK_COLOR = '#f59e0b';
const LIGHT_BG = '#f9fafb';

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: LIGHT_BG,
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0,
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
    justifyContent: 'space-between',
    gap: 12,
  },
  operationButton: {
    width: Platform.OS === "web" ? "20%" : '48%',
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  pushButton: {
    backgroundColor: PUSH_COLOR,
  },
  popButton: {
    backgroundColor: POP_COLOR,
  },
  peekButton: {
    backgroundColor: PEEK_COLOR,
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
  stackContainer: {
    alignItems: 'center',
  },
  stack: {
    alignItems: 'center',
    marginBottom: 20,
  },
  stackItem: {
    width: STACK_WIDTH,
    height: BOX_HEIGHT,
    backgroundColor: PRIMARY_COLOR,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginVertical: BOX_MARGIN / 2,
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 4 },
    position: 'relative',
  },
  topItem: {
    backgroundColor: PUSH_COLOR,
    borderWidth: 3,
    borderColor: '#059669',
  },
  selectedItem: {
    backgroundColor: PEEK_COLOR,
    borderWidth: 3,
    borderColor: '#d97706',
  },
  itemValue: {
    fontSize: 20,
    fontWeight: '800',
    color: 'white',
  },
  topLabel: {
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
  stackBase: {
    width: STACK_WIDTH + 40,
    height: 4,
    backgroundColor: '#374151',
    borderRadius: 2,
    marginTop: 10,
  },
  baseText: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'center',
    marginTop: 8,
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