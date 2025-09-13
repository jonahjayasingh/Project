import React, { useState, useRef } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  StatusBar,
  Alert,
  Animated,
  Easing,
  Platform
} from 'react-native';

type Node = {
  value: number;
  next: Node | null;
  id: string;
};

export const CircularSingleLinkedList = () => {
  const [head, setHead] = useState<Node | null>(null);
  const [inputValue, setInputValue] = useState('');
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [operation, setOperation] = useState<string | null>(null);
  const [status, setStatus] = useState('Create your first node to start');
  const [isAnimating, setIsAnimating] = useState(false);
  const animation = useRef(new Animated.Value(0)).current;

  // Generate unique ID for each node
  const generateId = () => Math.random().toString(36).substr(2, 9);

  // Convert circular list to array for rendering
  const listToArray = (): Node[] => {
    const arr: Node[] = [];
    if (!head) return arr;

    let current = head;
    let count = 0;
    const maxNodes = 20; // Safety limit for circular lists

    do {
      arr.push(current);
      current = current.next!;
      count++;
    } while (current !== head && count < maxNodes);

    return arr;
  };

  // Get list size
  const getSize = (): number => {
    if (!head) return 0;
    
    let count = 1;
    let current = head;
    while (current.next !== head) {
      count++;
      current = current.next!;
    }
    return count;
  };

  // Append to end
  const append = () => {
    const val = parseInt(inputValue);
    if (isNaN(val)) {
      Alert.alert('Invalid input', 'Please enter a valid number');
      return;
    }

    const newNode: Node = {
      value: val,
      next: head,
      id: generateId()
    };

    if (!head) {
      newNode.next = newNode;
      setHead(newNode);
      setStatus(`Created circular list with value ${val}`);
    } else {
      let current = head;
      while (current.next !== head) {
        current = current.next!;
      }
      current.next = newNode;
      setStatus(`Appended ${val} to the end`);
    }

    setOperation('append');
    setSelectedNode(newNode.id);
    setInputValue('');
    animateOperation();
  };

  // Prepend to start
  const prepend = () => {
    const val = parseInt(inputValue);
    if (isNaN(val)) {
      Alert.alert('Invalid input', 'Please enter a valid number');
      return;
    }

    const newNode: Node = {
      value: val,
      next: head,
      id: generateId()
    };

    if (!head) {
      newNode.next = newNode;
      setHead(newNode);
      setStatus(`Created circular list with value ${val}`);
    } else {
      // Find the tail to update its next pointer
      let tail = head;
      while (tail.next !== head) {
        tail = tail.next!;
      }
      tail.next = newNode;
      setHead(newNode);
      setStatus(`Prepended ${val} to the start`);
    }

    setOperation('prepend');
    setSelectedNode(newNode.id);
    setInputValue('');
    animateOperation();
  };

  // Remove value
  const remove = () => {
    const val = parseInt(inputValue);
    if (isNaN(val)) {
      Alert.alert('Invalid input', 'Please enter a valid number');
      return;
    }

    if (!head) {
      setStatus('List is empty');
      return;
    }

    // Single node case
    if (head.next === head) {
      if (head.value === val) {
        setHead(null);
        setStatus(`Removed the only node with value ${val}`);
        setSelectedNode(null);
        return;
      }
    }

    let current = head;
    let prev: Node | null = null;
    let found = false;

    do {
      if (current.value === val) {
        found = true;
        break;
      }
      prev = current;
      current = current.next!;
    } while (current !== head);

    if (!found) {
      Alert.alert('Not found', `Value ${val} not found in the list`);
      return;
    }

    if (current === head) {
      // Find tail to update its next pointer
      let tail = head;
      while (tail.next !== head) {
        tail = tail.next!;
      }
      tail.next = head.next;
      setHead(head.next);
    } else if (prev) {
      prev.next = current.next;
    }

    setStatus(`Removed node with value ${val}`);
    setSelectedNode(null);
    setInputValue('');
    animateOperation();
  };

  // Find value
  const find = () => {
    const val = parseInt(inputValue);
    if (isNaN(val)) {
      Alert.alert('Invalid input', 'Please enter a valid number');
      return;
    }

    if (!head) {
      setStatus('List is empty');
      return;
    }

    let current = head;
    let position = 0;

    do {
      if (current.value === val) {
        setStatus(`Found ${val} at position ${position}`);
        setSelectedNode(current.id);
        setOperation('find');
        animateOperation();
        return;
      }
      current = current.next!;
      position++;
    } while (current !== head);

    setStatus(`Value ${val} not found`);
    setSelectedNode(null);
  };

  // Clear list
  const clearList = () => {
    setHead(null);
    setStatus('Cleared the circular list');
    setSelectedNode(null);
  };

  // Animation for operations
  const animateOperation = () => {
    setIsAnimating(true);
    animation.setValue(0);
    Animated.timing(animation, {
      toValue: 1,
      duration: 500,
      easing: Easing.out(Easing.ease),
      useNativeDriver: true,
    }).start(() => setIsAnimating(false));
  };

  // Render circular list visualization
  const renderList = () => {
    const nodes = listToArray();
    const size = getSize();

    if (size === 0) {
      return (
        <View style={styles.emptyState}>
          <Text style={styles.emptyText}>⭕ List is empty</Text>
          <Text style={styles.emptySubtext}>Add nodes to create a circular list</Text>
        </View>
      );
    }

    return (
      <ScrollView 
        horizontal 
        contentContainerStyle={styles.listContainer}
        showsHorizontalScrollIndicator={false}
      >
        {nodes.map((node, index) => (
          <View key={node.id} style={styles.nodeGroup}>
            <Animated.View
              style={[
                styles.nodeBox,
                selectedNode === node.id && styles.selectedNode,
                index === 0 && styles.headNode,
                {
                  transform: [
                    {
                      scale: selectedNode === node.id
                        ? animation.interpolate({
                            inputRange: [0, 0.5, 1],
                            outputRange: [1, 1.2, 1.1]
                          })
                        : 1
                    }
                  ]
                }
              ]}
            >
              <Text style={styles.nodeValue}>{node.value}</Text>
              {index === 0 && <Text style={styles.nodeLabel}>HEAD</Text>}
            </Animated.View>

            {index < nodes.length - 1 ? (
              <View style={styles.arrowContainer}>
                <View style={styles.arrowLine} />
                <Text style={styles.arrow}>→</Text>
              </View>
            ) : (
              <View style={styles.circularArrowContainer}>
                <Text style={styles.circularArrow}>↻</Text>
                <Text style={styles.circularText}>back to head</Text>
              </View>
            )}
          </View>
        ))}
      </ScrollView>
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.header}>🔄 Circular Singly Linked List</Text>
        <Text style={styles.subtitle}>Visualize circular node connections</Text>

        <View style={styles.statsContainer}>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>List Size</Text>
            <Text style={styles.statValue}>{getSize()}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Status</Text>
            <Text style={styles.statValue}>
              {head ? 'Circular' : 'Empty'}
            </Text>
          </View>
        </View>

        <View style={styles.inputSection}>
          <Text style={styles.sectionTitle}>Node Operations</Text>
          
          <TextInput
            style={styles.input}
            placeholder="Enter value"
            value={inputValue}
            onChangeText={setInputValue}
            keyboardType="numeric"
          />

          <View style={styles.buttonGrid}>
            <TouchableOpacity 
              style={[styles.operationButton, styles.appendButton]}
              onPress={append}
              disabled={isAnimating}
            >
              <Text style={styles.buttonText}>Append</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.operationButton, styles.prependButton]}
              onPress={prepend}
              disabled={isAnimating}
            >
              <Text style={styles.buttonText}>Prepend</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.operationButton, styles.removeButton]}
              onPress={remove}
              disabled={isAnimating}
            >
              <Text style={styles.buttonText}>Remove</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.operationButton, styles.findButton]}
              onPress={find}
              disabled={isAnimating}
            >
              <Text style={styles.buttonText}>Find</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.operationButton, styles.clearButton]}
              onPress={clearList}
            >
              <Text style={styles.buttonText}>Clear List</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.statusContainer}>
          <Text style={styles.status}>{status}</Text>
        </View>

        <View style={styles.visualizationSection}>
          <Text style={styles.sectionTitle}>Circular List Visualization</Text>
          {renderList()}
        </View>

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>📖 About Circular Singly Linked List:</Text>
          <Text style={styles.infoText}>
            • Last node points back to the first node{'\n'}
            • No null pointers in the list{'\n'}
            • Efficient for circular data structures{'\n'}
            • Used in round-robin scheduling, buffers{'\n'}
            • Traversal requires careful termination condition
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const PRIMARY_COLOR = '#2563eb';
const APPEND_COLOR = '#10b981';
const PREPEND_COLOR = '#f59e0b';
const REMOVE_COLOR = '#ef4444';
const FIND_COLOR = '#8b5cf6';
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
      display: 'flex'
    })
  },
  operationButton: {
    width: Platform.OS === 'web' ? '20%': "48%",
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  appendButton: {
    backgroundColor: APPEND_COLOR,
  },
  prependButton: {
    backgroundColor: PREPEND_COLOR,
  },
  removeButton: {
    backgroundColor: REMOVE_COLOR,
  },
  findButton: {
    backgroundColor: FIND_COLOR,
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
  },
  visualizationSection: {
    marginBottom: 24,
  },
  listContainer: {
    padding: 16,
    alignItems: 'center',
  },
  nodeGroup: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  nodeBox: {
    backgroundColor: PRIMARY_COLOR,
    width: 70,
    height: 70,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 8,
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 4 },
  },
  headNode: {
    backgroundColor: '#7c3aed',
  },
  selectedNode: {
    backgroundColor: FIND_COLOR,
  },
  nodeValue: {
    color: 'white',
    fontWeight: '800',
    fontSize: 18,
  },
  nodeLabel: {
    color: 'white',
    fontSize: 10,
    fontWeight: '600',
    marginTop: 4,
  },
  arrowContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 30,
  },
  arrowLine: {
    width: 20,
    height: 2,
    backgroundColor: '#374151',
  },
  arrow: {
    color: '#374151',
    fontSize: 16,
    fontWeight: 'bold',
  },
  circularArrowContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 80,
  },
  circularArrow: {
    color: PRIMARY_COLOR,
    fontSize: 24,
    fontWeight: 'bold',
  },
  circularText: {
    color: '#6b7280',
    fontSize: 12,
    marginTop: 4,
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
});