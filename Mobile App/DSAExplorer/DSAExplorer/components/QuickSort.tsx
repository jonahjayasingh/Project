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
} from 'react-native';

const BOX_SIZE = 70;
const BOX_MARGIN = 12;
const { width } = Dimensions.get('window');
const NUM_COLUMNS = Math.floor(width / (BOX_SIZE + BOX_MARGIN));

export function QuickSort() {
  const [arrayInput, setArrayInput] = useState('5,3,8,4,2,7,1,6');
  const [array, setArray] = useState<number[]>([]);
  const [status, setStatus] = useState('Ready to sort');
  const [isSorting, setIsSorting] = useState(false);
  const [highlighted, setHighlighted] = useState<number[]>([]);
  const [pivotIndex, setPivotIndex] = useState<number | null>(null);
  const [sortedIndices, setSortedIndices] = useState<number[]>([]);
  const [speed, setSpeed] = useState(1000);

  const steps = useRef<
    { type: 'compare' | 'swap' | 'pivot' | 'done'; indices: number[] }[]
  >([]);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

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

  const generateQuickSortSteps = (arr: number[]) => {
    const actions: typeof steps.current = [];

    const quickSort = (low: number, high: number) => {
      if (low < high) {
        const pi = partition(low, high);
        quickSort(low, pi - 1);
        quickSort(pi + 1, high);
      } else if (low === high) {
        actions.push({ type: 'done', indices: [low] });
      }
    };

    const partition = (low: number, high: number): number => {
      const pivot = arr[high];
      actions.push({ type: 'pivot', indices: [high] });

      let i = low;
      for (let j = low; j < high; j++) {
        actions.push({ type: 'compare', indices: [j, high] });
        if (arr[j] < pivot) {
          if (i !== j) {
            [arr[i], arr[j]] = [arr[j], arr[i]];
            actions.push({ type: 'swap', indices: [i, j] });
          }
          i++;
        }
      }

      [arr[i], arr[high]] = [arr[high], arr[i]];
      actions.push({ type: 'swap', indices: [i, high] });
      actions.push({ type: 'done', indices: [i] });

      return i;
    };

    quickSort(0, arr.length - 1);
    return actions;
  };

  const startSort = () => {
    if (intervalRef.current) clearInterval(intervalRef.current);

    const parsed = parseInputArray(arrayInput);
    if (parsed.length < 2) {
      setStatus('⚠️ Enter at least 2 numbers.');
      return;
    }

    setArray(parsed);
    setIsSorting(true);
    setSortedIndices([]);
    setHighlighted([]);
    setPivotIndex(null);
    setStatus('⚡ Quick sort in progress...');

    const arrCopy = [...parsed];
    steps.current = generateQuickSortSteps(arrCopy);

    intervalRef.current = setInterval(() => {
      if (steps.current.length === 0) {
        clearInterval(intervalRef.current!);
        setIsSorting(false);
        setSortedIndices(Array.from({ length: arrCopy.length }, (_, i) => i));
        setStatus('🎉 Array sorted!');
        return;
      }

      const step = steps.current.shift()!;
      switch (step.type) {
        case 'compare':
          setHighlighted(step.indices);
          setStatus(`Comparing ${step.indices[0]} and ${step.indices[1]}`);
          break;
        case 'swap':
          const newArray = [...arrCopy];
          const [i, j] = step.indices;
          [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
          arrCopy[i] = newArray[i];
          arrCopy[j] = newArray[j];
          setArray([...newArray]);
          setStatus(`Swapping ${i} and ${j}`);
          break;
        case 'pivot':
          setPivotIndex(step.indices[0]);
          setStatus(`Choosing pivot at index ${step.indices[0]}`);
          break;
        case 'done':
          setSortedIndices((prev) => [...prev, ...step.indices]);
          setStatus(`Index ${step.indices[0]} sorted`);
          break;
      }
    }, speed);
  };

  const resetSort = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    setIsSorting(false);
    setSortedIndices([]);
    setHighlighted([]);
    setPivotIndex(null);
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

  const saveBookmark = () => {
    if (!arrayInput) {
      Alert.alert('Cannot bookmark', 'Please enter array first.');
      return;
    }
    Alert.alert(
      'Bookmark Saved',
      `Array: [${arrayInput}]\nSpeed: ${speed} ms`,
      [{ text: 'OK' }]
    );
  };

  const getSpeedLabel = (speed: number) => {
    if (speed === 2000) return '🐢 Very Slow';
    if (speed === 1000) return '🚶 Slow';
    if (speed === 500) return '🏃 Medium';
    if (speed === 250) return '⚡ Fast';
    return `${speed}ms`;
  };

  const renderItem = ({ item, index }: { item: number; index: number }) => {
    const isPivot = pivotIndex === index;
    const isHighlighted = highlighted.includes(index);
    const isSorted = sortedIndices.includes(index);

    return (
      <View
        style={[
          styles.box,
          isPivot && styles.pivotBox,
          isHighlighted && styles.compareBox,
          isSorted && styles.sortedBox,
        ]}
      >
        <Text
          style={[
            styles.boxText,
            (isPivot || isHighlighted || isSorted) && styles.boxTextActive,
          ]}
        >
          {item}
        </Text>
        <Text style={styles.indexText}>{index}</Text>
        {isPivot && <Text style={styles.labelText}>pivot</Text>}
        {isHighlighted && <Text style={styles.labelText}>comparing</Text>}
        {isSorted && <Text style={styles.labelText}>sorted</Text>}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        <Text style={styles.header}>⚡ Quick Sort Visualizer</Text>

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
                  <TouchableOpacity
          style={[styles.actionBtn,styles.bookmarkButton, isSorting && styles.btnDisabled]}
          onPress={saveBookmark}
          disabled={isSorting}
        >
          <Text style={styles.bookmarkText}>🔖 Bookmark</Text>
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
              scrollEnabled={false}
              contentContainerStyle={styles.flatListContent}
            />
          </View>
        )}

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>📖 About Quick Sort:</Text>
          <Text style={styles.infoText}>
            • ⚡ Efficient divide-and-conquer sorting algorithm{'\n'}
            • ⏱️ Time Complexity: O(n log n) average, O(n²) worst case{'\n'}
            • 💾 Space Complexity: O(log n) - logarithmic space{'\n'}
            • 🎯 In-place algorithm that works well for large datasets{'\n'}
            • 📊 Selects a pivot and partitions the array around it
          </Text>
        </View>

        <View style={styles.legendCard}>
          <Text style={styles.legendTitle}>Legend:</Text>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.pivotBox]} />
            <Text style={styles.legendText}>Pivot element</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.compareBox]} />
            <Text style={styles.legendText}>Elements being compared</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.sortedBox]} />
            <Text style={styles.legendText}>Sorted elements</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.box]} />
            <Text style={styles.legendText}>Unsorted elements</Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const PRIMARY_COLOR = '#2563eb';
const COMPARE_COLOR = '#f59e0b';
const PIVOT_COLOR = '#8b5cf6';
const SORTED_COLOR = '#10b981';
const LIGHT_BG = '#f9fafb';

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: LIGHT_BG,
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
    color: '6b7280',
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
  },
  actionBtn: {
    paddingVertical: 15,
    paddingHorizontal: 20,
    borderRadius: 12,
    alignItems: 'center',
    minWidth: 110,
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
  bookmarkButton: {
    backgroundColor: '#f59e0b',
    // padding: 15,
    borderRadius: 12,
    alignItems: 'center',
    // marginBottom: 16,
  },
  bookmarkText: {
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
    backgroundColor: 'white',
    margin: BOX_MARGIN / 2,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: PRIMARY_COLOR,
    position: 'relative',
  },
  compareBox: {
    backgroundColor: COMPARE_COLOR,
    borderColor: COMPARE_COLOR,
    transform: [{ scale: 1.1 }],
  },
  pivotBox: {
    backgroundColor: PIVOT_COLOR,
    borderColor: PIVOT_COLOR,
    transform: [{ scale: 1.1 }],
  },
  sortedBox: {
    backgroundColor: SORTED_COLOR,
    borderColor: SORTED_COLOR,
    transform: [{ scale: 1.05 }],
  },
  boxText: {
    fontSize: 20,
    fontWeight: '700',
    color: PRIMARY_COLOR,
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
  labelText: {
    position: 'absolute',
    bottom: 4,
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
    marginBottom: 12,
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
    borderColor: PRIMARY_COLOR,
  },
  legendText: {
    fontSize: 14,
    color: '#374151',
    fontWeight: '500',
  },
});