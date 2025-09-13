import React, { useState, useEffect, useRef } from 'react';
import {
  SafeAreaView,
  ScrollView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  StatusBar,
  Alert,
} from 'react-native';

type TreeNode = {
  val: number;
  left: TreeNode | null;
  right: TreeNode | null;
};

// Build tree from level-order array (without nulls)
const buildTree = (arr: number[], i = 0): TreeNode | null => {
  if (i >= arr.length) return null;
  return {
    val: arr[i],
    left: buildTree(arr, 2 * i + 1),
    right: buildTree(arr, 2 * i + 2),
  };
};

// BFS (Level Order) traversal
const bfsLevelOrder = (root: TreeNode | null): TreeNode[] => {
  const result: TreeNode[] = [];
  if (!root) return result;

  const queue: TreeNode[] = [root];
  
  while (queue.length > 0) {
    const current = queue.shift()!;
    result.push(current);
    
    if (current.left) queue.push(current.left);
    if (current.right) queue.push(current.right);
  }
  
  return result;
};

// Generate random tree array without null values
const generateRandomTreeArray = (size: number): number[] => {
  const arr: number[] = [];
  for (let i = 0; i < size; i++) {
    arr.push(Math.floor(Math.random() * 100) + 1);
  }
  return arr;
};

// Calculate tree height for layout
const getTreeHeight = (node: TreeNode | null): number => {
  if (!node) return 0;
  return 1 + Math.max(getTreeHeight(node.left), getTreeHeight(node.right));
};

export function BFSVisualizer() {
  const [input, setInput] = useState('1,2,3,4,5,6,7');
  const [root, setRoot] = useState<TreeNode | null>(null);
  const [order, setOrder] = useState<TreeNode[]>([]);
  const [currentIdx, setCurrentIdx] = useState(-1);
  const [speed, setSpeed] = useState(1000);
  const [isPlaying, setIsPlaying] = useState(false);
  const timer = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    try {
      const parsed = input
        .split(',')
        .map((s) => parseInt(s.trim()))
        .filter((n) => !isNaN(n));
      
      const tree = buildTree(parsed);
      setRoot(tree);
      resetTraversal();
    } catch (e) {
      setRoot(null);
    }
  }, [input]);

  const start = () => {
    if (!root) {
      Alert.alert('Invalid Tree', 'Please enter a valid tree array.');
      return;
    }
    const seq = bfsLevelOrder(root);
    setOrder(seq);
    setCurrentIdx(-1);
    setIsPlaying(true);
    
    if (timer.current) clearInterval(timer.current);
    
    setTimeout(() => {
      setCurrentIdx(0);
      timer.current = setInterval(() => {
        setCurrentIdx((i) => {
          if (i + 1 >= seq.length) {
            if (timer.current) clearInterval(timer.current);
            setIsPlaying(false);
            return i;
          }
          return i + 1;
        });
      }, speed);
    }, 300);
  };

  const resetTraversal = () => {
    if (timer.current) clearInterval(timer.current);
    setOrder([]);
    setCurrentIdx(-1);
    setIsPlaying(false);
  };

  const generateRandomTree = () => {
    const arr = generateRandomTreeArray(7); // Generate 7 nodes for a good visual
    setInput(arr.join(','));
  };

  // Render tree as text with proper indentation
  const renderTreeText = (node: TreeNode | null, prefix = '', isLeft = true): string => {
    if (!node) return '';
    
    let result = '';
    const connector = isLeft ? '└── ' : '├── ';
    const newPrefix = prefix + (isLeft ? '    ' : '│   ');
    
    const idx = order.findIndex(n => n === node);
    let status = '';
    if (idx === currentIdx) status = ' 🟡';
    else if (idx !== -1 && idx < currentIdx) status = ' ✅';
    
    result += prefix + connector + node.val + status + '\n';
    
    if (node.right) {
      result += renderTreeText(node.right, newPrefix, false);
    }
    if (node.left) {
      result += renderTreeText(node.left, newPrefix, true);
    }
    
    return result;
  };

  const treeHeight = getTreeHeight(root);
  const isCompleteTree = order.length > 0;

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        <Text style={styles.header}>🔄 BFS Tree Visualizer</Text>

        <Text style={styles.label}>Enter tree nodes (comma-separated numbers):</Text>
        <TextInput
          style={styles.input}
          value={input}
          onChangeText={setInput}
          placeholder="e.g. 1,2,3,4,5,6,7"
          placeholderTextColor="#9ca3af"
          keyboardType="numbers-and-punctuation"
        />

        <View style={styles.controls}>
          <View style={styles.speedSection}>
            <Text style={styles.speedLabel}>Animation Speed:</Text>
            <View style={styles.speedButtons}>
              {[250, 500, 1000, 2000].map((spd) => (
                <TouchableOpacity
                  key={spd}
                  style={[
                    styles.speedBtn,
                    speed === spd && styles.speedBtnActive,
                    isPlaying && styles.speedBtnDisabled
                  ]}
                  onPress={() => setSpeed(spd)}
                  disabled={isPlaying}
                >
                  <Text style={[
                    styles.speedBtnText,
                    speed === spd && styles.speedBtnTextActive
                  ]}>
                    {spd === 250 ? '⚡ Fast' : 
                     spd === 500 ? '🏃 Medium' : 
                     spd === 1000 ? '🚶 Slow' : 
                     '🐢 Very Slow'}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          <View style={styles.actionSection}>
            <TouchableOpacity 
              style={[styles.actionBtn, styles.startBtn, (!root || isPlaying) && styles.btnDisabled]} 
              onPress={start}
              disabled={!root || isPlaying}
            >
              <Text style={styles.btnText}>▶️ Start BFS</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={[styles.actionBtn, styles.resetBtn]} 
              onPress={resetTraversal}
            >
              <Text style={styles.btnText}>🔄 Reset</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={[styles.actionBtn, styles.randomBtn]} 
              onPress={generateRandomTree}
            >
              <Text style={styles.btnText}>🎲 Random Tree</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.statusCard}>
          <Text style={styles.statusText}>
            {currentIdx === -1 ? 'Ready to start BFS traversal' : 
             currentIdx >= order.length ? '✅ Traversal completed!' : 
             `🔍 Visiting node: ${order[currentIdx]?.val}`}
          </Text>
        </View>

        {order.length > 0 && (
          <View style={styles.progressCard}>
            <Text style={styles.progressText}>
              Progress: {Math.min(currentIdx + 1, order.length)}/{order.length} nodes
            </Text>
            <View style={styles.progressBar}>
              <View style={[
                styles.progressFill, 
                { width: `${((Math.min(currentIdx + 1, order.length)) / order.length) * 100}%` }
              ]} />
            </View>
          </View>
        )}

        {root && (
          <View style={styles.treeCard}>
            <Text style={styles.treeTitle}>Tree Structure (Height: {treeHeight}):</Text>
            <View style={styles.treeContainer}>
              <Text style={styles.treeText}>
                {renderTreeText(root)}
              </Text>
            </View>
          </View>
        )}

        {order.length > 0 && (
          <View style={styles.traversalCard}>
            <Text style={styles.traversalTitle}>BFS Traversal Path (Level Order):</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <View style={styles.traversalPath}>
                {order.map((node, index) => (
                  <View key={index} style={styles.pathItem}>
                    <Text style={[
                      styles.nodeValue,
                      index === currentIdx && styles.currentNodeValue,
                      index < currentIdx && styles.visitedNodeValue
                    ]}>
                      {node.val}
                    </Text>
                    {index < order.length - 1 && (
                      <Text style={styles.arrow}>→</Text>
                    )}
                  </View>
                ))}
              </View>
            </ScrollView>
          </View>
        )}

        <View style={styles.legendCard}>
          <Text style={styles.legendTitle}>Legend:</Text>
          <View style={styles.legendItem}>
            <Text style={styles.legendEmoji}>🟡</Text>
            <Text style={styles.legendText}>Current node being visited</Text>
          </View>
          <View style={styles.legendItem}>
            <Text style={styles.legendEmoji}>✅</Text>
            <Text style={styles.legendText}>Already visited nodes</Text>
          </View>
          <View style={styles.legendItem}>
            <Text style={styles.legendEmoji}>→</Text>
            <Text style={styles.legendText}>Traversal direction</Text>
          </View>
        </View>

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>📖 About BFS (Breadth-First Search):</Text>
          <Text style={styles.infoText}>
            • 🌳 Explores all nodes at the current depth before moving to the next level{'\n'}
            • 🎯 Uses a queue data structure (FIFO - First In First Out){'\n'}
            * 🔍 Visits nodes level by level from left to right{'\n'}
            • ⚡ Time Complexity: O(n) where n is number of nodes{'\n'}
            • 💾 Space Complexity: O(w) where w is maximum width{'\n'}
            • 🗺️ Perfect for finding shortest paths in unweighted graphs{'\n'}
            • 📊 Current tree height: {treeHeight} levels
          </Text>
        </View>

        
      </ScrollView>
    </SafeAreaView>
  );
}

// Tailwind CSS-like styles
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
    paddingTop: StatusBar.currentHeight || 20,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 40,
  },
  header: {
    fontSize: 28,
    fontWeight: '800',
    textAlign: 'center',
    marginBottom: 24,
    color: '#2563eb',
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#374151',
  },
  input: {
    height: 50,
    borderWidth: 2,
    borderColor: '#e5e7eb',
    borderRadius: 12,
    paddingHorizontal: 16,
    marginBottom: 20,
    backgroundColor: 'white',
    fontSize: 16,
    color: '#1f2937',
  },
  controls: {
    marginBottom: 20,
  },
  speedSection: {
    marginBottom: 16,
  },
  speedLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
    color: '#374151',
  },
  speedButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 5,
    justifyContent: 'center',
  },
  speedBtn: {
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
    backgroundColor: '#f3f4f6',
    borderWidth: 2,
    borderColor: 'transparent',
    minWidth: 50,
    alignItems: 'center',
  },
  speedBtnActive: {
    backgroundColor: '#2563eb',
    borderColor: '#2563eb',
  },
  speedBtnDisabled: {
    opacity: 0.6,
  },
  speedBtnText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6b7280',
  },
  speedBtnTextActive: {
    color: 'white',
  },
  actionSection: {
    flexDirection: 'row',
    gap: 12,
    justifyContent: 'center',
  },
  actionBtn: {
    paddingVertical: 15,
    paddingHorizontal: 20,
    borderRadius: 12,
    alignItems: 'center',
    minWidth: 110,
  },
  startBtn: {
    backgroundColor: '#2563eb',
  },
  resetBtn: {
    backgroundColor: '#6b7280',
  },
  randomBtn: {
    backgroundColor: '#8b5cf6',
  },
  btnDisabled: {
    opacity: 0.5,
  },
  btnText: {
    color: 'white',
    fontWeight: '700',
    fontSize: 14,
  },
  statusCard: {
    backgroundColor: '#dbeafe',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#2563eb',
  },
  statusText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e40af',
    textAlign: 'center',
  },
  progressCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: '#e5e7eb',
  },
  progressText: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
    color: '#374151',
    textAlign: 'center',
  },
  progressBar: {
    height: 8,
    backgroundColor: '#e5e7eb',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#2563eb',
    borderRadius: 4,
  },
  treeCard: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: '#e5e7eb',
  },
  treeTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 12,
    color: '#2563eb',
    textAlign: 'center',
  },
  treeContainer: {
    backgroundColor: '#f8fafc',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  treeText: {
    fontSize: 16,
    fontFamily: 'monospace',
    lineHeight: 24,
    color: '#1f2937',
  },
  traversalCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: '#e5e7eb',
  },
  traversalTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 12,
    color: '#2563eb',
    textAlign: 'center',
  },
  traversalPath: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#f8fafc',
    borderRadius: 8,
  },
  pathItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  nodeValue: {
    fontSize: 16,
    fontWeight: '600',
    padding: 10,
    backgroundColor: '#f3f4f6',
    borderRadius: 8,
    minWidth: 45,
    textAlign: 'center',
    color: '#6b7280',
  },
  currentNodeValue: {
    backgroundColor: '#f59e0b',
    color: 'white',
    transform: [{ scale: 1.1 }],
  },
  visitedNodeValue: {
    backgroundColor: '#10b981',
    color: 'white',
  },
  arrow: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#9ca3af',
    marginHorizontal: 8,
  },
  legendCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: '#e5e7eb',
  },
  legendTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 12,
    color: '#2563eb',
    textAlign: 'center',
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    paddingHorizontal: 8,
  },
  legendEmoji: {
    fontSize: 18,
    marginRight: 12,
    width: 28,
  },
  legendText: {
    fontSize: 14,
    color: '#374151',
    fontWeight: '500',
  },
  infoCard: {
    backgroundColor: '#f0f9ff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#2563eb',
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 12,
    color: '#2563eb',
  },
  infoText: {
    fontSize: 14,
    lineHeight: 22,
    color: '#374151',
  },
  statsCard: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#e5e7eb',
  },
  statsTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 16,
    color: '#2563eb',
    textAlign: 'center',
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: '800',
    color: '#2563eb',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#6b7280',
    fontWeight: '600',
  },
});