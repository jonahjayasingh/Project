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
  Animated,
  Dimensions,
  Platform
} from 'react-native';

const { width } = Dimensions.get('window');

type TreeNode = {
  val: number;
  left: TreeNode | null;
  right: TreeNode | null;
  id: string;
};

// Build tree from level-order array
const buildTree = (arr: (number | null)[], i = 0): TreeNode | null => {
  if (i >= arr.length || arr[i] === null) return null;
  return {
    val: arr[i] as number,
    left: buildTree(arr, 2 * i + 1),
    right: buildTree(arr, 2 * i + 2),
    id: Math.random().toString(36).substr(2, 9),
  };
};

// Postorder traversal collecting nodes
const postorderTraversal = (root: TreeNode | null, result: TreeNode[] = []) => {
  if (!root) return result;
  postorderTraversal(root.left, result);
  postorderTraversal(root.right, result);
  result.push(root);
  return result;
};

// Generate random tree array with null values
const generateRandomTreeArray = (size: number) => {
  const arr: (number | null)[] = [];
  for (let i = 0; i < size; i++) {
    arr.push(Math.floor(Math.random() * 100) + 1);
  }
  // Ensure root is never null
  if (arr[0] === null) arr[0] = Math.floor(Math.random() * 100) + 1;
  return arr;
};

export function PostorderTraversalVisualizer() {
  const [input, setInput] = useState('1,2,3,4,5,10,7');
  const [root, setRoot] = useState<TreeNode | null>(null);
  const [order, setOrder] = useState<TreeNode[]>([]);
  const [currentIdx, setCurrentIdx] = useState(-1);
  const [speed, setSpeed] = useState(1000);
  const [isPlaying, setIsPlaying] = useState(false);
  const timer = useRef<NodeJS.Timeout | null>(null);
  const animation = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    try {
      const arr = input
        .split(',')
        .map((s) => (s.trim().toLowerCase() === 'null' ? null : Number(s.trim())))
        .filter((n) => n === null || !isNaN(n));
      
      const tree = buildTree(arr);
      setRoot(tree);
      resetTraversal();
    } catch (e) {
      Alert.alert('Error', 'Invalid tree input format');
    }
  }, [input]);

  const startTraversal = () => {
    if (!root) {
      Alert.alert('Invalid Tree', 'Please enter a valid tree array.');
      return;
    }
    const seq = postorderTraversal(root, []);
    setOrder(seq);
    setCurrentIdx(-1);
    setIsPlaying(true);
    
    if (timer.current) clearInterval(timer.current);
    
    setTimeout(() => {
      setCurrentIdx(0);
      animateNode();
      timer.current = setInterval(() => {
        setCurrentIdx((i) => {
          if (i + 1 >= seq.length) {
            if (timer.current) clearInterval(timer.current);
            setIsPlaying(false);
            return i;
          }
          animateNode();
          return i + 1;
        });
      }, speed);
    }, 300);
  };

  const animateNode = () => {
    animation.setValue(0);
    Animated.timing(animation, {
      toValue: 1,
      duration: 500,
      useNativeDriver: true,
    }).start();
  };

  const resetTraversal = () => {
    if (timer.current) clearInterval(timer.current);
    setOrder([]);
    setCurrentIdx(-1);
    setIsPlaying(false);
  };

  const generateRandomTree = () => {
    const arr = generateRandomTreeArray(10);
    setInput(arr.map(v => v === null ? 'null' : v.toString()).join(','));
  };

  // Render tree as text with proper indentation
  const renderTreeText = (node: TreeNode | null, prefix = '', isLeft = true): string => {
    if (!node) return '';
    
    let result = '';
    const connector = isLeft ? '└── ' : '├── ';
    const newPrefix = prefix + (isLeft ? '    ' : '│   ');
    
    const idx = order.findIndex(n => n.id === node.id);
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

  const getSpeedLabel = (speed: number) => {
    if (speed === 250) return '⚡ Fast';
    if (speed === 500) return '🏃 Medium';
    if (speed === 1000) return '🚶 Slow';
    if (speed === 2000) return '🐢 Very Slow';
    return `${speed}ms`;
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        <Text style={styles.header}>🌿 Postorder Traversal Visualizer</Text>
        <Text style={styles.subtitle}>Left → Right → Root</Text>

        <View style={styles.inputSection}>
          <Text style={styles.sectionTitle}>Tree Input</Text>
          <Text style={styles.inputHint}>
            Enter level-order values (comma-separated, use "null" for empty nodes):
          </Text>
          <TextInput
            style={styles.input}
            placeholder="e.g. 1,2,3,4,5,null,7"
            value={input}
            onChangeText={setInput}
            editable={!isPlaying}
          />
        </View>

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
                  {getSpeedLabel(spd)}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.controls}>
          <TouchableOpacity
            style={[styles.controlButton, styles.startButton, (!root || isPlaying) && styles.buttonDisabled]}
            onPress={startTraversal}
            disabled={!root || isPlaying}
          >
            <Text style={styles.buttonText}>▶️ Start Traversal</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.controlButton, styles.resetButton, !isPlaying && currentIdx === -1 && styles.buttonDisabled]}
            onPress={resetTraversal}
            disabled={!isPlaying && currentIdx === -1}
          >
            <Text style={styles.buttonText}>🔄 Reset</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.controlButton, styles.randomButton]}
            onPress={generateRandomTree}
          >
            <Text style={styles.buttonText}>🎲 Random Tree</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.statusContainer}>
          <Text style={styles.status}>
            {currentIdx === -1 ? 'Ready to start postorder traversal' : 
             currentIdx >= order.length ? '✅ Traversal completed!' : 
             `🔍 Visiting node: ${order[currentIdx]?.val}`}
          </Text>
          {order.length > 0 && (
            <Text style={styles.progress}>
              Progress: {Math.min(currentIdx + 1, order.length)}/{order.length} nodes
            </Text>
          )}
        </View>

        {order.length > 0 && (
          <View style={styles.progressCard}>
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
            <Text style={styles.treeTitle}>Tree Structure:</Text>
            <View style={styles.treeContainer}>
              <Text style={styles.treeText}>
                {renderTreeText(root)}
              </Text>
            </View>
          </View>
        )}

        {order.length > 0 && (
          <View style={styles.traversalCard}>
            <Text style={styles.traversalTitle}>Postorder Traversal Path:</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <View style={styles.traversalPath}>
                {order.map((node, index) => (
                  <Animated.View 
                    key={node.id} 
                    style={[
                      styles.pathItem,
                      {
                        transform: [
                          {
                            scale: index === currentIdx
                              ? animation.interpolate({
                                  inputRange: [0, 0.5, 1],
                                  outputRange: [1, 1.3, 1.1]
                                })
                              : 1
                          }
                        ]
                      }
                    ]}
                  >
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
                  </Animated.View>
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
          <Text style={styles.infoTitle}>📖 About Postorder Traversal:</Text>
          <Text style={styles.infoText}>
            • 🌿 Order: Left subtree → Right subtree → Root{'\n'}
            • 🎯 Useful for deleting trees and expression evaluation{'\n'}
            • ⚡ Time Complexity: O(n) where n is number of nodes{'\n'}
            • 💾 Space Complexity: O(h) where h is height of tree{'\n'}
            • 📊 Uses: Tree deletion, postfix expression evaluation{'\n'}
            • 🔍 Algorithm: Recursively traverse left, traverse right, visit root
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const PRIMARY_COLOR = '#2563eb';
const CURRENT_COLOR = '#f59e0b';
const VISITED_COLOR = '#10b981';
const LIGHT_BG = '#f9fafb';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: LIGHT_BG,
    paddingTop: StatusBar.currentHeight,
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
    color: PRIMARY_COLOR,
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    marginBottom: 24,
    textAlign: 'center',
  },
  inputSection: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: PRIMARY_COLOR,
    marginBottom: 10,
  },
  inputHint: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 8,
  },
  input: {
    height: 50,
    borderWidth: 2,
    borderColor: '#e5e7eb',
    borderRadius: 12,
    paddingHorizontal: 16,
    fontSize: 16,
    backgroundColor: 'white',
    color: '#1f2937',
  },
  speedSection: {
    marginBottom: 20,
  },
  speedLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 12,
  },
  speedButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    justifyContent: 'center',
  },
  speedBtn: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    backgroundColor: '#f3f4f6',
    borderWidth: 1,
    borderColor: 'transparent',
  },
  speedBtnActive: {
    backgroundColor: PRIMARY_COLOR,
    borderColor: PRIMARY_COLOR,
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
  controls: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 12,
    marginBottom: 20,
  },
  controlButton: {
    flex: 1,
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
    minWidth: 110,
    ...(Platform.OS === "web" &&{
      maxWidth: "20%"
    })
  },
  startButton: {
    backgroundColor: PRIMARY_COLOR,
  },
  resetButton: {
    backgroundColor: '#6b7280',
  },
  randomButton: {
    backgroundColor: '#8b5cf6',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonText: {
    color: 'white',
    fontWeight: '700',
    fontSize: 14,
  },
  statusContainer: {
    backgroundColor: '#e0e7ff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
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
  progress: {
    fontSize: 14,
    color: '#6366f1',
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
  progressBar: {
    height: 8,
    backgroundColor: '#e5e7eb',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: PRIMARY_COLOR,
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
    color: PRIMARY_COLOR,
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
    color: PRIMARY_COLOR,
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
    backgroundColor: CURRENT_COLOR,
    color: 'white',
  },
  visitedNodeValue: {
    backgroundColor: VISITED_COLOR,
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
    color: PRIMARY_COLOR,
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
    borderLeftWidth: 4,
    borderLeftColor: PRIMARY_COLOR,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 12,
    color: PRIMARY_COLOR,
  },
  infoText: {
    fontSize: 14,
    lineHeight: 22,
    color: '#374151',
  },
});