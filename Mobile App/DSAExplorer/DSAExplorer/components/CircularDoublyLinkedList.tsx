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
  Dimensions,Platform
} from 'react-native';

const { width } = Dimensions.get('window');

type DoublyNode = {
  value: number;
  next: DoublyNode | null;
  prev: DoublyNode | null;
  id: string;
};

export const CircularDoublyLinkedListVisualizer = () => {
  const [head, setHead] = useState<DoublyNode | null>(null);
  const [tail, setTail] = useState<DoublyNode | null>(null);
  const [inputValue, setInputValue] = useState('');
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [operation, setOperation] = useState<string | null>(null);
  const [status, setStatus] = useState('Create your first node to start');
  const [traversalDirection, setTraversalDirection] = useState<'forward' | 'backward'>('forward');
  const [isAnimating, setIsAnimating] = useState(false);
  const animation = useRef(new Animated.Value(0)).current;

  // Generate unique ID for each node
  const generateId = () => Math.random().toString(36).substr(2, 9);

  // Convert circular list to array for rendering
  const listToArray = (): DoublyNode[] => {
    const arr: DoublyNode[] = [];
    if (!head) return arr;

    let current = head;
    let count = 0;
    const maxNodes = 20; // Safety limit

    do {
      arr.push(current);
      current = traversalDirection === 'forward' ? current.next! : current.prev!;
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

    const newNode: DoublyNode = {
      value: val,
      next: head,
      prev: tail,
      id: generateId()
    };

    if (!head) {
      newNode.next = newNode;
      newNode.prev = newNode;
      setHead(newNode);
      setTail(newNode);
      setStatus(`Created circular list with value ${val}`);
    } else {
      newNode.prev = tail;
      newNode.next = head;
      
      tail!.next = newNode;
      head!.prev = newNode;
      
      setTail(newNode);
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

    const newNode: DoublyNode = {
      value: val,
      next: head,
      prev: tail,
      id: generateId()
    };

    if (!head) {
      newNode.next = newNode;
      newNode.prev = newNode;
      setHead(newNode);
      setTail(newNode);
      setStatus(`Created circular list with value ${val}`);
    } else {
      newNode.next = head;
      newNode.prev = tail;
      
      head!.prev = newNode;
      tail!.next = newNode;
      
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

    let current = head;
    let found = false;
    let count = 0;

    do {
      if (current.value === val) {
        found = true;
        break;
      }
      current = current.next!;
      count++;
    } while (current !== head && count < getSize());

    if (!found) {
      Alert.alert('Not found', `Value ${val} not found in the list`);
      return;
    }

    // Single node case
    if (getSize() === 1) {
      setHead(null);
      setTail(null);
      setStatus(`Removed the only node with value ${val}`);
      setSelectedNode(null);
      return;
    }

    current.prev!.next = current.next;
    current.next!.prev = current.prev;

    if (current === head) {
      setHead(current.next);
    }
    if (current === tail) {
      setTail(current.prev);
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
    let count = 0;

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
      count++;
    } while (current !== head && count < getSize());

    setStatus(`Value ${val} not found`);
    setSelectedNode(null);
  };

  // Clear list
  const clearList = () => {
    setHead(null);
    setTail(null);
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
          <Text style={styles.emptySubtext}>Add nodes to create a circular doubly linked list</Text>
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
            {/* Left arrow for previous pointer */}
            {index > 0 && (
              <View style={styles.arrowContainer}>
                <Text style={styles.doubleArrow}>⇄</Text>
              </View>
            )}

            <Animated.View
              style={[
                styles.nodeBox,
                selectedNode === node.id && styles.selectedNode,
                index === 0 && styles.headNode,
                index === nodes.length - 1 && styles.tailNode,
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
              {index === nodes.length - 1 && <Text style={styles.nodeLabel}>TAIL</Text>}
            </Animated.View>

            {/* Circular connection indicator */}
            {index === nodes.length - 1 && (
              <View style={styles.circularContainer}>
                <Text style={styles.circularArrow}>↻</Text>
                <Text style={styles.circularText}>circular connection</Text>
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
        <Text style={styles.header}>🔄 Circular Doubly Linked List</Text>
        <Text style={styles.subtitle}>Bidirectional circular node connections</Text>

        <View style={styles.statsContainer}>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>List Size</Text>
            <Text style={styles.statValue}>{getSize()}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Traversal</Text>
            <TouchableOpacity onPress={() => setTraversalDirection(
              traversalDirection === 'forward' ? 'backward' : 'forward'
            )}>
              <Text style={styles.traversalToggle}>
                {traversalDirection === 'forward' ? 'HEAD→TAIL' : 'TAIL→HEAD'}
              </Text>
            </TouchableOpacity>
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
              style={[styles.operationButton, styles.traversalButton]}
              onPress={() => setTraversalDirection(
                traversalDirection === 'forward' ? 'backward' : 'forward'
              )}
            >
              <Text style={styles.buttonText}>
                {traversalDirection === 'forward' ? 'Show ←' : 'Show →'}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.operationButton, styles.clearButton]}
              onPress={clearList}
            >
              <Text style={styles.buttonText}>Clear</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.statusContainer}>
          <Text style={styles.status}>{status}</Text>
          <Text style={styles.traversalInfo}>
            Viewing: {traversalDirection === 'forward' ? 'Forward (HEAD→TAIL)' : 'Backward (TAIL→HEAD)'}
          </Text>
        </View>

        <View style={styles.visualizationSection}>
          <Text style={styles.sectionTitle}>Circular Doubly Linked List</Text>
          {renderList()}
        </View>

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>📖 About Circular Doubly Linked List:</Text>
          <Text style={styles.infoText}>
            • Each node has pointers to both next and previous nodes{'\n'}
            • The list is circular: tail points to head and vice versa{'\n'}
            • Can be traversed in both directions{'\n'}
            • O(1) insertion/deletion at both ends{'\n'}
            • Used in advanced data structures and algorithms
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
const TRAVERSAL_COLOR = '#6366f1';
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
  traversalToggle: {
    fontSize: 16,
    fontWeight: '600',
    color: TRAVERSAL_COLOR,
    textDecorationLine: 'underline',
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
    width: Platform.OS === 'web'? '20%' : '48%',
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
  traversalButton: {
    backgroundColor: TRAVERSAL_COLOR,
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
  traversalInfo: {
    fontSize: 14,
    color: '#6366f1',
    textAlign: 'center',
    fontStyle: 'italic',
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
  tailNode: {
    backgroundColor: '#dc2626',
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
  doubleArrow: {
    color: '#374151',
    fontSize: 16,
    fontWeight: 'bold',
  },
  circularContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 100,
    marginLeft: 8,
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