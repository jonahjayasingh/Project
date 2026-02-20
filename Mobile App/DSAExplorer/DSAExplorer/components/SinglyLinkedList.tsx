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
  Platform,
} from 'react-native';

type ListNode = {
  value: number;
  next: ListNode | null;
  id: string;
};

export function SinglyLinkedList() {
  const [inputValue, setInputValue] = useState('');
  const [indexValue, setIndexValue] = useState('');
  const [head, setHead] = useState<ListNode | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [operation, setOperation] = useState<string | null>(null);
  const [status, setStatus] = useState('Create your first node to start');

  // Generate unique ID for each node
  const generateId = () => Math.random().toString(36).substr(2, 9);

  // Convert linked list to array for rendering
  const linkedListToArray = (node: ListNode | null): ListNode[] => {
    const arr: ListNode[] = [];
    let current = node;
    while (current !== null) {
      arr.push(current);
      current = current.next;
    }
    return arr;
  };

  // Insert at beginning
  const insertAtBeginning = () => {
    const val = parseInt(inputValue);
    if (isNaN(val)) {
      Alert.alert('Invalid input', 'Please enter a valid number');
      return;
    }

    const newNode: ListNode = { 
      value: val, 
      next: head,
      id: generateId()
    };

    setHead(newNode);
    setStatus(`Inserted ${val} at beginning`);
    setOperation('insert-begin');
    setSelectedNode(newNode.id);
    setInputValue('');
  };

  // Insert at end
  const insertAtEnd = () => {
    const val = parseInt(inputValue);
    if (isNaN(val)) {
      Alert.alert('Invalid input', 'Please enter a valid number');
      return;
    }

    const newNode: ListNode = { 
      value: val, 
      next: null,
      id: generateId()
    };

    if (head === null) {
      setHead(newNode);
      setStatus(`Inserted ${val} as head`);
    } else {
      let current: ListNode = head;
      while (current.next !== null) {
        current = current.next;
      }
      current.next = newNode;
      setHead({ ...head });
      setStatus(`Inserted ${val} at end`);
    }

    setOperation('insert-end');
    setSelectedNode(newNode.id);
    setInputValue('');
  };

  // Insert at specific position
  const insertAtPosition = () => {
    const val = parseInt(inputValue);
    const position = parseInt(indexValue);
    
    if (isNaN(val) || isNaN(position) || position < 0) {
      Alert.alert('Invalid input', 'Please enter valid number and position');
      return;
    }

    if (position === 0) {
      insertAtBeginning();
      return;
    }

    const newNode: ListNode = { 
      value: val, 
      next: null,
      id: generateId()
    };

    if (head === null) {
      Alert.alert('List is empty', 'Cannot insert at position');
      return;
    }

    let current: ListNode = head;
    let count = 0;
    
    while (current !== null && count < position - 1) {
      current = current.next!;
      count++;
    }

    if (current === null) {
      Alert.alert('Position out of bounds', 'Position exceeds list length');
      return;
    }

    newNode.next = current.next;
    current.next = newNode;
    setHead({ ...head });
    setStatus(`Inserted ${val} at position ${position}`);
    setOperation('insert-position');
    setSelectedNode(newNode.id);
    setInputValue('');
    setIndexValue('');
  };

  // Delete by value
  const deleteByValue = () => {
    const val = parseInt(inputValue);
    if (isNaN(val)) {
      Alert.alert('Invalid input', 'Please enter a valid number');
      return;
    }

    if (head === null) {
      setStatus('List is empty');
      return;
    }

    if (head.value === val) {
      setHead(head.next);
      setStatus(`Deleted head with value ${val}`);
      setInputValue('');
      return;
    }

    let current: ListNode = head;
    while (current.next !== null && current.next.value !== val) {
      current = current.next;
    }

    if (current.next === null) {
      setStatus(`Value ${val} not found`);
    } else {
      current.next = current.next.next;
      setHead({ ...head });
      setStatus(`Deleted node with value ${val}`);
    }
    setInputValue('');
  };

  // Search for value
  const searchByValue = () => {
    const val = parseInt(inputValue);
    if (isNaN(val)) {
      Alert.alert('Invalid input', 'Please enter a valid number');
      return;
    }

    if (head === null) {
      setStatus('List is empty');
      return;
    }

    let current: ListNode | null = head;
    let position = 0;
    
    while (current !== null && current.value !== val) {
      current = current.next;
      position++;
    }

    if (current === null) {
      setStatus(`Value ${val} not found`);
      setSelectedNode(null);
    } else {
      setStatus(`Found ${val} at position ${position}`);
      setSelectedNode(current.id);
    }
    setInputValue('');
  };

  // Clear entire list
  const clearList = () => {
    setHead(null);
    setStatus('Cleared the list');
    setSelectedNode(null);
  };

  // Render linked list visualization
  const renderLinkedList = () => {
    const nodes = linkedListToArray(head);
    
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
        {nodes.map((node, index) => (
          <View key={node.id} style={styles.nodeGroup}>
            <View
              style={[
                styles.nodeBox,
                selectedNode === node.id && styles.selectedNode,
                index === 0 && styles.headNode
              ]}
            >
              <Text style={styles.nodeValue}>{node.value}</Text>
              {index === 0 && <Text style={styles.nodeLabel}>HEAD</Text>}
            </View>
            
            <View style={styles.arrowContainer}>
              <View style={styles.arrowLine} />
              <Text style={styles.arrow}>→</Text>
            </View>
          </View>
        ))}
        
        {/* NULL node at the end */}
        <View style={styles.nodeGroup}>
          <View style={[styles.nodeBox, styles.nullNode]}>
            <Text style={styles.nodeValue}>NULL</Text>
          </View>
        </View>
      </ScrollView>
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.header}>🔗 Singly Linked List</Text>
        <Text style={styles.subtitle}>Visualize linked list operations</Text>

        <View style={styles.inputSection}>
          <Text style={styles.sectionTitle}>Node Operations</Text>
          
          <TextInput
            style={styles.input}
            placeholder="Enter value"
            value={inputValue}
            onChangeText={setInputValue}
            keyboardType="numeric"
          />

          <TextInput
            style={styles.input}
            placeholder="Position (for insert at)"
            value={indexValue}
            onChangeText={setIndexValue}
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
              style={[styles.operationButton, styles.insertButton]}
              onPress={insertAtPosition}
            >
              <Text style={styles.buttonText}>Insert at Position</Text>
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
          <Text style={styles.sectionTitle}>Linked List Visualization</Text>
          {renderLinkedList()}
        </View>

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>📖 About Singly Linked List:</Text>
          <Text style={styles.infoText}>
            • Each node contains data and a pointer to the next node{'\n'}
            • Insertion/Deletion: O(1) at beginning, O(n) at end{'\n'}
            • Access: O(n) time complexity{'\n'}
            • Dynamic size, efficient for frequent insertions/deletions{'\n'}
            • The list terminates with a NULL pointer
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
    marginBottom: 12,
    color: '#1f2937',
  },
  buttonGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-evenly',
    gap: 12,
    ...(Platform.OS === 'web' && {
      display: 'flex',
      flexWrap: "wrap"
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