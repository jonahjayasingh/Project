import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  SafeAreaView,
  StyleSheet,
  ScrollView,
  StatusBar,
  Alert,
  Platform
} from 'react-native';

type DoubleListNode = {
  value: number;
  prev: DoubleListNode | null;
  next: DoubleListNode | null;
  id: string;
};

export function DoubleLinkedList() {
  const [head, setHead] = useState<DoubleListNode | null>(null);
  const [tail, setTail] = useState<DoubleListNode | null>(null);
  const [inputValue, setInputValue] = useState('');
  const [indexValue, setIndexValue] = useState('');
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [operation, setOperation] = useState<string | null>(null);
  const [status, setStatus] = useState('Create your first node to start');
  const [traversalDirection, setTraversalDirection] = useState<'forward' | 'backward'>('forward');

  // Generate unique ID for each node
  const generateId = () => Math.random().toString(36).substr(2, 9);

  // Convert linked list to array for rendering
  const linkedListToArray = (startNode: DoubleListNode | null): DoubleListNode[] => {
    const arr: DoubleListNode[] = [];
    let current = startNode;
    while (current !== null) {
      arr.push(current);
      current = current.next;
    }
    return arr;
  };

  // Get list in reverse order
  const reverseListToArray = (endNode: DoubleListNode | null): DoubleListNode[] => {
    const arr: DoubleListNode[] = [];
    let current = endNode;
    while (current !== null) {
      arr.push(current);
      current = current.prev;
    }
    return arr;
  };

  // Insert at end
  const insertAtEnd = () => {
    const val = parseInt(inputValue);
    if (isNaN(val)) {
      Alert.alert('Invalid input', 'Please enter a valid number');
      return;
    }

    const newNode: DoubleListNode = {
      value: val,
      prev: tail,
      next: null,
      id: generateId()
    };

    if (!head) {
      setHead(newNode);
      setTail(newNode);
      setStatus(`Inserted ${val} as first node`);
    } else {
      tail!.next = newNode;
      setTail(newNode);
      setStatus(`Inserted ${val} at end`);
    }

    setOperation('insert-end');
    setSelectedNode(newNode.id);
    setInputValue('');
  };

  // Insert at beginning
  const insertAtBeginning = () => {
    const val = parseInt(inputValue);
    if (isNaN(val)) {
      Alert.alert('Invalid input', 'Please enter a valid number');
      return;
    }

    const newNode: DoubleListNode = {
      value: val,
      prev: null,
      next: head,
      id: generateId()
    };

    if (!head) {
      setHead(newNode);
      setTail(newNode);
      setStatus(`Inserted ${val} as first node`);
    } else {
      head.prev = newNode;
      setHead(newNode);
      setStatus(`Inserted ${val} at beginning`);
    }

    setOperation('insert-begin');
    setSelectedNode(newNode.id);
    setInputValue('');
  };

  // Delete by value
  const deleteByValue = () => {
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
    while (current !== null) {
      if (current.value === val) {
        // Node is head
        if (current === head) {
          setHead(current.next);
          if (current.next) {
            current.next.prev = null;
          } else {
            setTail(null);
          }
        }
        // Node is tail
        else if (current === tail) {
          setTail(current.prev);
          if (current.prev) {
            current.prev.next = null;
          }
        }
        // Node in middle
        else {
          if (current.prev) current.prev.next = current.next;
          if (current.next) current.next.prev = current.prev;
        }

        setStatus(`Deleted node with value ${val}`);
        setOperation('delete');
        setSelectedNode(null);
        setInputValue('');
        return;
      }
      current = current.next!;
    }

    Alert.alert('Not found', `Value ${val} not found in list`);
  };

  // Search for value
  const searchByValue = () => {
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
    while (current !== null) {
      if (current.value === val) {
        setStatus(`Found ${val} in the list`);
        setSelectedNode(current.id);
        setOperation('search');
        return;
      }
      current = current.next!;
    }

    setStatus(`Value ${val} not found`);
    setSelectedNode(null);
  };

  // Clear entire list
  const clearList = () => {
    setHead(null);
    setTail(null);
    setStatus('Cleared the list');
    setSelectedNode(null);
  };

  // Render linked list visualization
  const renderLinkedList = () => {
    const nodes = traversalDirection === 'forward' 
      ? linkedListToArray(head) 
      : reverseListToArray(tail);

    if (nodes.length === 0) {
      return (
        <View style={styles.emptyState}>
          <Text style={styles.emptyText}>📝 List is empty</Text>
          <Text style={styles.emptySubtext}>Add nodes to get started</Text>
        </View>
      );
    }

    return (
      <ScrollView 
        horizontal 
        contentContainerStyle={styles.listContainer}
        showsHorizontalScrollIndicator={false}
      >
        {/* NULL node at the beginning */}
        {traversalDirection === 'forward' && (
          <View style={styles.nodeGroup}>
            <View style={[styles.nodeBox, styles.nullNode]}>
              <Text style={styles.nodeValue}>NULL</Text>
            </View>
            <View style={styles.arrowContainer}>
              <View style={styles.arrowLine} />
              <Text style={styles.arrow}>⇄</Text>
            </View>
          </View>
        )}

        {nodes.map((node, index) => (
          <View key={node.id} style={styles.nodeGroup}>
            <View
              style={[
                styles.nodeBox,
                selectedNode === node.id && styles.selectedNode,
                index === 0 && (traversalDirection === 'forward' ? styles.headNode : styles.tailNode),
                index === nodes.length - 1 && (traversalDirection === 'forward' ? styles.tailNode : styles.headNode)
              ]}
            >
              <Text style={styles.nodeValue}>{node.value}</Text>
              {index === 0 && (
                <Text style={styles.nodeLabel}>
                  {traversalDirection === 'forward' ? 'HEAD' : 'TAIL'}
                </Text>
              )}
              {index === nodes.length - 1 && (
                <Text style={styles.nodeLabel}>
                  {traversalDirection === 'forward' ? 'TAIL' : 'HEAD'}
                </Text>
              )}
            </View>
            
            {index < nodes.length - 1 && (
              <View style={styles.arrowContainer}>
                <View style={styles.arrowLine} />
                <Text style={styles.arrow}>⇄</Text>
              </View>
            )}
          </View>
        ))}

        {/* NULL node at the end */}
        {traversalDirection === 'forward' && (
          <View style={styles.nodeGroup}>
            <View style={styles.arrowContainer}>
              <View style={styles.arrowLine} />
              <Text style={styles.arrow}>⇄</Text>
            </View>
            <View style={[styles.nodeBox, styles.nullNode]}>
              <Text style={styles.nodeValue}>NULL</Text>
            </View>
          </View>
        )}

        {/* For backward traversal, show NULL nodes in reverse order */}
        {traversalDirection === 'backward' && (
          <>
            <View style={styles.nodeGroup}>
              <View style={[styles.nodeBox, styles.nullNode]}>
                <Text style={styles.nodeValue}>NULL</Text>
              </View>
              <View style={styles.arrowContainer}>
                <View style={styles.arrowLine} />
                <Text style={styles.arrow}>⇄</Text>
              </View>
            </View>
            
            <View style={styles.nodeGroup}>
              <View style={styles.arrowContainer}>
                <View style={styles.arrowLine} />
                <Text style={styles.arrow}>⇄</Text>
              </View>
              <View style={[styles.nodeBox, styles.nullNode]}>
                <Text style={styles.nodeValue}>NULL</Text>
              </View>
            </View>
          </>
        )}
      </ScrollView>
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.header}>🔗 Double Linked List</Text>
        <Text style={styles.subtitle}>Visualize bidirectional node connections</Text>

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
              style={[styles.operationButton, styles.insertButton]}
              onPress={insertAtBeginning}
            >
              <Text style={styles.buttonText}>Insert at Start</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.operationButton, styles.insertButton]}
              onPress={insertAtEnd}
            >
              <Text style={styles.buttonText}>Insert at End</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.operationButton, styles.deleteButton]}
              onPress={deleteByValue}
            >
              <Text style={styles.buttonText}>Delete by Value</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.operationButton, styles.searchButton]}
              onPress={searchByValue}
            >
              <Text style={styles.buttonText}>Search Value</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.operationButton, styles.traversalButton]}
              onPress={() => setTraversalDirection(
                traversalDirection === 'forward' ? 'backward' : 'forward'
              )}
            >
              <Text style={styles.buttonText}>
                {traversalDirection === 'forward' ? 'Show Backward' : 'Show Forward'}
              </Text>
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
          <Text style={styles.traversalInfo}>
            Currently viewing: {traversalDirection === 'forward' ? 'HEAD → TAIL' : 'TAIL → HEAD'}
          </Text>
        </View>

        <View style={styles.visualizationSection}>
          <Text style={styles.sectionTitle}>Linked List Visualization</Text>
          {renderLinkedList()}
        </View>

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>📖 About Double Linked List:</Text>
          <Text style={styles.infoText}>
            • Each node has pointers to both next and previous nodes{'\n'}
            • Can be traversed in both directions{'\n'}
            • Insertion/Deletion: O(1) at both ends, O(n) in middle{'\n'}
            • More memory usage but flexible traversal{'\n'}
            • The list terminates with NULL pointers at both ends
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const PRIMARY_COLOR = '#2563eb';
const INSERT_COLOR = '#10b981';
const DELETE_COLOR = '#ef4444';
const SEARCH_COLOR = '#f59e0b';
const TRAVERSAL_COLOR = '#8b5cf6';
const NULL_COLOR = '#6b7280';
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
    ...(Platform.OS === 'web' && {
      display: 'flex'
    })
  },
  operationButton: {
    width: Platform.OS == 'web' ? '20%' : '48%',
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  insertButton: {
    backgroundColor: INSERT_COLOR,
  },
  deleteButton: {
    backgroundColor: DELETE_COLOR,
  },
  searchButton: {
    backgroundColor: SEARCH_COLOR,
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
    width: 80,
    height: 80,
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
  nullNode: {
    backgroundColor: NULL_COLOR,
  },
  selectedNode: {
    backgroundColor: SEARCH_COLOR,
    transform: [{ scale: 1.1 }],
  },
  nodeValue: {
    color: 'white',
    fontWeight: '800',
    fontSize: 20,
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