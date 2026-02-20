import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Alert,
  StyleSheet,
  SafeAreaView,
  FlatList,
  Dimensions,
  ScrollView,
  Platform,
  StatusBar
} from 'react-native';

let BOX_SIZE: number;
let BOX_MARGIN: number;
let NUM_COLUMNS: number;

if (Platform.OS !== "web") {
  BOX_MARGIN = 5;
  const { width } = Dimensions.get('window');
  NUM_COLUMNS = 5;  
  BOX_SIZE = Math.floor((width - (NUM_COLUMNS + 10) * BOX_MARGIN) / NUM_COLUMNS);
} else {
  BOX_SIZE = 80;
  BOX_MARGIN = 4;
  const { width } = Dimensions.get('window');
  NUM_COLUMNS = Math.floor(width / (BOX_SIZE + BOX_MARGIN));
}

export function MergeSort() {
  const [arrayInput, setArrayInput] = useState('5,3,8,4,2,7,1,6');
  const [array, setArray] = useState<number[]>([]);
  const [status, setStatus] = useState('Ready to sort');
  const [isSorting, setIsSorting] = useState(false);
  const [sortedIndices, setSortedIndices] = useState<number[]>([]);
  const [comparingIndices, setComparingIndices] = useState<number[]>([]);
  const [swappingIndices, setSwappingIndices] = useState<number[]>([]);
  const [speed, setSpeed] = useState(1000);

  const steps = useRef<{ 
    type: 'compare' | 'swap' | 'merge' | 'sortedHalf'; 
    indices: number[]; 
    values?: number[];
  }[]>([]);
  const currentArray = useRef<number[]>([]);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const totalSteps = useRef(0);
  const currentStepIndex = useRef(0);

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  const parseInputArray = (input: string): number[] => {
    return input
      .split(',')
      .map((item) => parseInt(item.trim()))
      .filter((num) => !isNaN(num));
  };

  const generateMergeSortSteps = (arr: number[]) => {
    const tempSteps: typeof steps.current = [];
    const originalArray = [...arr];

    const merge = (left: number, mid: number, right: number) => {
      let i = left;
      let j = mid + 1;
      const tempArray = [...originalArray];

      for (let k = left; k <= right; k++) {
        if (i > mid) {
          // Take from right side
          tempSteps.push({
            type: 'swap',
            indices: [k, j],
            values: [tempArray[j], tempArray[k]]
          });
          originalArray[k] = tempArray[j];
          j++;
        } else if (j > right) {
          // Take from left side
          tempSteps.push({
            type: 'swap',
            indices: [k, i],
            values: [tempArray[i], tempArray[k]]
          });
          originalArray[k] = tempArray[i];
          i++;
        } else {
          // Compare both sides
          tempSteps.push({ 
            type: 'compare', 
            indices: [i, j]
          });
          
          if (tempArray[i] <= tempArray[j]) {
            // Take from left side
            tempSteps.push({
              type: 'swap',
              indices: [k, i],
              values: [tempArray[i], tempArray[k]]
            });
            originalArray[k] = tempArray[i];
            i++;
          } else {
            // Take from right side
            tempSteps.push({
              type: 'swap',
              indices: [k, j],
              values: [tempArray[j], tempArray[k]]
            });
            originalArray[k] = tempArray[j];
            j++;
          }
        }
      }

      // Mark the merged segment as sorted
      tempSteps.push({
        type: 'merge',
        indices: Array.from({ length: right - left + 1 }, (_, idx) => left + idx)
      });
    };

    const mergeSortRecursive = (left: number, right: number) => {
      if (left >= right) {
        // Single element is always sorted
        tempSteps.push({
          type: 'sortedHalf',
          indices: [left]
        });
        return;
      }
      
      const mid = Math.floor((left + right) / 2);
      
      // Sort left half
      mergeSortRecursive(left, mid);
      
      // Mark left half as sorted
      tempSteps.push({
        type: 'sortedHalf',
        indices: Array.from({ length: mid - left + 1 }, (_, idx) => left + idx)
      });
      
      // Sort right half
      mergeSortRecursive(mid + 1, right);
      
      // Mark right half as sorted
      tempSteps.push({
        type: 'sortedHalf',
        indices: Array.from({ length: right - mid }, (_, idx) => mid + 1 + idx)
      });
      
      // Merge both halves
      merge(left, mid, right);
    };

    mergeSortRecursive(0, arr.length - 1);
    return tempSteps;
  };

  const startSort = () => {
    if (intervalRef.current) clearInterval(intervalRef.current);

    const parsed = parseInputArray(arrayInput);
    if (parsed.length < 2) {
      setStatus('⚠️ Enter at least 2 numbers.');
      return;
    }

    setArray(parsed);
    currentArray.current = [...parsed];
    setIsSorting(true);
    setSortedIndices([]);
    setComparingIndices([]);
    setSwappingIndices([]);
    setStatus('🔄 Running merge sort...');

    const arrCopy = [...parsed];
    steps.current = generateMergeSortSteps([...arrCopy]);
    totalSteps.current = steps.current.length;
    currentStepIndex.current = 0;

    let stepIndex = 0;
    intervalRef.current = setInterval(() => {
      if (stepIndex >= steps.current.length) {
        clearInterval(intervalRef.current!);
        setIsSorting(false);
        setSortedIndices(Array.from({ length: arrCopy.length }, (_, i) => i));
        setComparingIndices([]);
        setSwappingIndices([]);
        setStatus('🎉 Array sorted!');
        return;
      }

      const step = steps.current[stepIndex];
      stepIndex++;
      currentStepIndex.current = stepIndex;

      if (step.type === 'compare') {
        setComparingIndices(step.indices);
        setSwappingIndices([]);
        setStatus(`🔍 Comparing ${currentArray.current[step.indices[0]]} and ${currentArray.current[step.indices[1]]}`);
      } else if (step.type === 'swap') {
        setComparingIndices([]);
        setSwappingIndices(step.indices);
        
        // Perform the actual swap instantly
        const newArray = [...currentArray.current];
        const [index1, index2] = step.indices;
        const [value1, value2] = step.values!;
        
        // Swap the values instantly
        newArray[index1] = value1;
        newArray[index2] = value2;
        
        currentArray.current = newArray;
        setArray([...newArray]);
        
        setStatus(`🔄 Swapping ${value2} with ${value1} between positions ${index1} and ${index2}`);
      } else if (step.type === 'merge') {
        setComparingIndices([]);
        setSwappingIndices([]);
        setSortedIndices(prev => [...new Set([...prev, ...step.indices])]);
        setStatus(`✅ Merged segment completed`);
      } else if (step.type === 'sortedHalf') {
        setComparingIndices([]);
        setSwappingIndices([]);
        setSortedIndices(prev => [...new Set([...prev, ...step.indices])]);
        
        if (step.indices.length === 1) {
          setStatus(`✅ Single element ${currentArray.current[step.indices[0]]} at position ${step.indices[0]} is sorted`);
        } else {
          setStatus(`✅ Half segment [${step.indices[0]}-${step.indices[step.indices.length-1]}] is now sorted`);
        }
      }
    }, speed);
  };

  const resetSort = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    setIsSorting(false);
    setSortedIndices([]);
    setComparingIndices([]);
    setSwappingIndices([]);
    setStatus('Ready to sort');
  };

  const generateRandomArray = () => {
    const randomArray = Array.from({ length: 8 }, () => 
      Math.floor(Math.random() * 20) + 1
    );
    
    setArrayInput(randomArray.join(','));
    resetSort();
  };

  const changeSpeed = (newSpeed: number) => {
    setSpeed(newSpeed);
    if (isSorting && intervalRef.current) {
      resetSort();
      setTimeout(startSort, 100);
    }
  };

  const getSpeedLabel = (speed: number) => {
    if (speed === 2000) return '🐢 Very Slow';
    if (speed === 1000) return '🚶 Slow';
    if (speed === 500) return '🏃 Medium';
    if (speed === 250) return '⚡ Fast';
    return `${speed}ms`;
  };

  const renderItem = ({ item, index }: { item: number; index: number }) => {
    const isComparing = comparingIndices.includes(index);
    const isSwapping = swappingIndices.includes(index);
    const isSorted = sortedIndices.includes(index);

    let backgroundColor = UNSORTED_COLOR;
    let borderColor = UNSORTED_COLOR;

    if (isComparing) {
      backgroundColor = COMPARING_COLOR;
      borderColor = COMPARING_COLOR;
    } else if (isSwapping) {
      backgroundColor = SWAPPING_COLOR;
      borderColor = SWAPPING_COLOR;
    } else if (isSorted) {
      backgroundColor = SORTED_COLOR;
      borderColor = SORTED_COLOR;
    }

    return (
      <View
        style={[
          styles.box,
          { backgroundColor, borderColor }
        ]}
      >
        <Text
          style={[
            styles.boxText,
            (isComparing || isSwapping || isSorted) && styles.boxTextActive,
          ]}
        >
          {item}
        </Text>
        <Text style={styles.indexText}>{index}</Text>
        <View style={styles.labelContainer}>
          {isComparing && <Text style={styles.labelText}>comparing</Text>}
          {isSwapping && <Text style={styles.labelText}>swapping</Text>}
          {isSorted && !isComparing && !isSwapping && <Text style={styles.labelText}>sorted</Text>}
        </View>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        <Text style={styles.header}>🔗 Merge Sort Visualizer</Text>

        <Text style={styles.label}>Enter array (comma-separated numbers):</Text>
        <TextInput
          placeholder="e.g. 5,3,8,4,2,7,1,6"
          value={arrayInput}
          onChangeText={setArrayInput}
          style={[styles.input, isSorting && styles.inputDisabled]}
          editable={!isSorting}
          keyboardType="numbers-and-punctuation"
        />

       

        <View style={styles.speedSection}>
          <Text style={styles.speedLabel}>Animation Speed:</Text>
          <View style={styles.speedButtons}>
            {[250, 500, 1000, 2000].map((spd) => (
              <TouchableOpacity
                key={spd}
                style={[
                  styles.speedBtn,
                  speed === spd && styles.speedBtnActive,
                  isSorting && styles.speedBtnDisabled
                ]}
                onPress={() => changeSpeed(spd)}
                disabled={isSorting}
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

        <View style={styles.actionSection}>
          <TouchableOpacity 
            style={[styles.actionBtn, styles.startBtn, isSorting && styles.btnDisabled]} 
            onPress={startSort}
            disabled={isSorting}
          >
            <Text style={styles.btnText}>▶️ Start Sort</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.actionBtn, styles.resetBtn]} 
            onPress={resetSort}
          >
            <Text style={styles.btnText}>🔄 Reset</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.actionBtn, styles.randomBtn, isSorting && styles.btnDisabled]} 
            onPress={generateRandomArray}
            disabled={isSorting}
          >
            <Text style={styles.btnText}>🎲 Random</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.statusCard}>
          <Text style={styles.statusText}>{status}</Text>
        </View>

        {array.length > 0 && (
          <View style={styles.arrayContainer}>
            <Text style={styles.arrayTitle}>Array Visualization:</Text>
            <FlatList
              data={array}
              renderItem={renderItem}
              keyExtractor={(_, idx) => idx.toString()}
              numColumns={NUM_COLUMNS}
              scrollEnabled={true}
              contentContainerStyle={styles.flatListContent}
            />
          </View>
        )}

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>📖 About Merge Sort:</Text>
          <Text style={styles.infoText}>
            • 🔗 Efficient divide-and-conquer sorting algorithm{'\n'}
            • ⏱️ Time Complexity: O(n log n) - linearithmic time{'\n'}
            • 💾 Space Complexity: O(n) - linear space{'\n'}
            • 🎯 Stable algorithm that works well for large datasets{'\n'}
            • 📊 Divides array into halves, sorts them, then merges back{'\n'}
            • 🎨 Colors show current operation: comparing, swapping, or sorted
          </Text>
        </View>

        <View style={styles.legendCard}>
          <Text style={styles.legendTitle}>Color Legend:</Text>
          
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: COMPARING_COLOR }]} />
            <Text style={styles.legendText}>Comparing elements</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: SWAPPING_COLOR }]} />
            <Text style={styles.legendText}>Swapping elements</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: SORTED_COLOR }]} />
            <Text style={styles.legendText}>Sorted elements</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: UNSORTED_COLOR }]} />
            <Text style={styles.legendText}>Unsorted elements</Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

// Updated color scheme with red for swapping and yellow for comparing
const COMPARING_COLOR = '#fbbf24';   // Yellow for comparing
const SWAPPING_COLOR = '#ef4444';    // Red for swapping
const SORTED_COLOR = '#10b981';      // Green for sorted
const UNSORTED_COLOR = '#6b7280';    // Gray for unsorted
const PRIMARY_COLOR = '#2563eb';
const LIGHT_BG = '#f9fafb';

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: LIGHT_BG,
    paddingTop: Platform.OS === 'ios' ? 0 : StatusBar.currentHeight,
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
    textAlign: 'center',
    marginBottom: 24,
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
    fontSize: 16,
    backgroundColor: 'white',
    marginBottom: 16,
    color: '#1f2937',
  },
  inputDisabled: {
    backgroundColor: '#f3f4f6',
    color: '#6b7280',
  },
  progressSection: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: '#e5e7eb',
  },
  progressLabel: {
    fontSize: 16,
    fontWeight: '700',
    color: PRIMARY_COLOR,
    marginBottom: 8,
    textAlign: 'center',
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
    gap: 8,
    justifyContent: 'center',
  },
  speedBtn: {
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
    backgroundColor: '#f3f4f6',
    borderWidth: 2,
    borderColor: 'transparent',
    minWidth: 100,
    alignItems: 'center',
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
  actionSection: {
    flexDirection: 'row',
    gap: 12,
    justifyContent: 'center',
    marginBottom: 16,
    flexWrap: 'wrap'
  },
  actionBtn: {
    paddingVertical: 15,
    paddingHorizontal: 20,
    borderRadius: 12,
    alignItems: 'center',
    minWidth: 110,
    marginHorizontal: 4,
    marginVertical: 4,
  },
  startBtn: {
    backgroundColor: PRIMARY_COLOR,
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
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: PRIMARY_COLOR,
  },
  statusText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e40af',
    textAlign: 'center',
  },
  arrayContainer: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
    borderWidth: 2,
    borderColor: '#e5e7eb',
    alignItems: 'center',
  },
  arrayTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 16,
    color: PRIMARY_COLOR,
    textAlign: 'center',
  },
  flatListContent: {
    justifyContent: 'center',
  },
  box: {
    width: BOX_SIZE,
    height: BOX_SIZE,
    margin: BOX_MARGIN / 2,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    position: 'relative',
  },
  boxText: {
    fontSize: 20,
    fontWeight: '700',
    color: LIGHT_BG,
    
  },
  boxTextActive: {
    color: 'white',
  },
  indexText: {
    position: 'absolute',
    top: 4,
    fontSize: 10,
    fontWeight: '600',
    color: '#6b7280',
  },
  labelContainer: {
    position: 'absolute',
    bottom: 4,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  labelText: {
    fontSize: 10,
    fontWeight: '600',
    color: 'white',
    backgroundColor: 'rgba(0,0,0,0.3)',
    paddingHorizontal: 4,
    borderRadius: 4,
  },
  infoCard: {
    backgroundColor: '#f0f9ff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 16,
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
    lineHeight: 20,
    color: '#374151',
  },
  legendCard: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#e5e7eb',
  },
  legendTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 16,
    color: PRIMARY_COLOR,
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
    borderColor: '#e5e7eb',
  },
  legendText: {
    fontSize: 14,
    color: '#374151',
    fontWeight: '500',
  },
});