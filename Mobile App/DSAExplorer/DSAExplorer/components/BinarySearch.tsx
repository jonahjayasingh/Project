import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  Dimensions,
  Alert,
  StatusBar,
  ScrollView,
  Platform
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

const BOX_SIZE = 70;
const BOX_MARGIN = 6;
const { width } = Dimensions.get('window');
const NUM_COLUMNS = Math.floor(width / (BOX_SIZE + BOX_MARGIN));

export function BinarySearch() {
  const [arrayInput, setArrayInput] = useState('1,3,5,7,9,11,13,15,17,19');
  const [targetInput, setTargetInput] = useState('7');
  const [speed, setSpeed] = useState(1000);
  const [array, setArray] = useState<number[]>([]);
  const [status, setStatus] = useState('Ready to search');
  const [low, setLow] = useState<number | null>(null);
  const [high, setHigh] = useState<number | null>(null);
  const [mid, setMid] = useState<number | null>(null);
  const [foundIndex, setFoundIndex] = useState<number | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  const isArraySorted = (arr: number[]): boolean => {
    for (let i = 1; i < arr.length; i++) {
      if (arr[i] < arr[i - 1]) {
        return false;
      }
    }
    return true;
  };

  const parseInputArray = (input: string): number[] => {
    return input
      .split(',')
      .map((item) => parseInt(item.trim()))
      .filter((num) => !isNaN(num));
  };

  const clearExistingInterval = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const validateInputs = (parsedArray: number[], target: number): boolean => {
    setError(null);
    
    if (parsedArray.length === 0) {
      setError('⚠️ Please enter a valid array with at least one number');
      return false;
    }
    
    if (isNaN(target)) {
      setError('⚠️ Please enter a valid target number');
      return false;
    }
    
    if (!isArraySorted(parsedArray)) {
      setError('❌ Array must be sorted in ascending order for binary search');
      return false;
    }
    
    return true;
  };

  const startSearch = () => {
    clearExistingInterval();
    setError(null);

    const parsedArray = parseInputArray(arrayInput);
    const sortedArray = [...parsedArray].sort((a, b) => a - b);
    const target = parseInt(targetInput.trim());

    if (!validateInputs(parsedArray, target)) {
      return;
    }

    // Check if the array is already sorted as entered
    const isSorted = isArraySorted(parsedArray);
    if (!isSorted) {
      setArray(sortedArray);
      setStatus('🔍 Using sorted version of input array for search...');
      Alert.alert(
        'Array Not Sorted',
        'Binary search requires a sorted array. Your input has been sorted automatically for the search.',
        [{ text: 'OK' }]
      );
    } else {
      setArray(parsedArray);
      setStatus('🔍 Starting binary search...');
    }

    setLow(0);
    setHigh(sortedArray.length - 1);
    setMid(null);
    setFoundIndex(null);
    setIsSearching(true);

    let l = 0;
    let h = sortedArray.length - 1;

    intervalRef.current = setInterval(() => {
      if (l > h) {
        clearExistingInterval();
        setStatus(`❌ Target ${target} not found.`);
        setMid(null);
        setLow(null);
        setHigh(null);
        setIsSearching(false);
        return;
      }

      const m = Math.floor((l + h) / 2);
      setLow(l);
      setHigh(h);
      setMid(m);
      setStatus(`Checking middle index ${m}: ${sortedArray[m]} (range: [${l} - ${h}])`);

      if (sortedArray[m] === target) {
        clearExistingInterval();
        setFoundIndex(m);
        setStatus(`🎉 Target ${target} found at index ${m}!`);
        setIsSearching(false);
      } else if (sortedArray[m] < target) {
        l = m + 1;
      } else {
        h = m - 1;
      }
    }, speed);
  };

  const resetSearch = () => {
    clearExistingInterval();
    setIsSearching(false);
    setLow(null);
    setHigh(null);
    setMid(null);
    setFoundIndex(null);
    setError(null);
    setStatus('Ready to search');
  };

  const generateRandomArray = () => {
    const size = Math.floor(Math.random() * 10) + 5; // 5-14 elements
    const randomArray = Array.from({ length: size }, () => 
      Math.floor(Math.random() * 100) + 1
    ).sort((a, b) => a - b);
    
    const randomTarget = randomArray[Math.floor(Math.random() * randomArray.length)];
    
    setArrayInput(randomArray.join(','));
    setTargetInput(randomTarget.toString());
    setError(null);
    resetSearch();
  };

  const handleArrayInputChange = (text: string) => {
    setArrayInput(text);
    setError(null);
  };

  const changeSpeed = (newSpeed: number) => {
    setSpeed(newSpeed);
    if (isSearching && intervalRef.current) {
      resetSearch();
      setTimeout(startSearch, 100);
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
    const isLow = index === low;
    const isHigh = index === high;
    const isMid = index === mid;
    const isFound = index === foundIndex;

    return (
      <View
        style={[
          styles.box,
          isFound && styles.foundBox,
          isMid && !isFound && styles.midBox,
          (isLow || isHigh) && !isFound && styles.rangeBox,
        ]}
      >
        <Text
          style={[
            styles.boxText,
            (isFound || isMid || isLow || isHigh) && styles.boxTextActive,
          ]}
        >
          {item}
        </Text>
        <Text style={styles.indexText}>{index}</Text>
        
        {/* Show only one label at a time with priority: found > mid > low/high */}
        <View style={styles.labelContainer}>
          {isFound && <Text style={styles.labelText}>found</Text>}
          {!isFound && isMid && <Text style={styles.labelText}>mid</Text>}
          {!isFound && isLow && <Text style={styles.labelText}>low</Text>}
          {!isFound && isHigh && <Text style={styles.labelText}>high</Text>}
        </View>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        <Text style={styles.header}>🔍 Binary Search Visualizer</Text>

        <Text style={styles.label}>Enter sorted array (comma-separated numbers):</Text>
        <TextInput
          placeholder="e.g. 1,3,5,7,9,11,13,15,17,19"
          value={arrayInput}
          onChangeText={handleArrayInputChange}
          style={[styles.input, isSearching && styles.inputDisabled, error && styles.inputError]}
          editable={!isSearching}
          keyboardType="numbers-and-punctuation"
        />
        {error && <Text style={styles.errorText}>{error}</Text>}

        <Text style={styles.label}>Enter target number:</Text>
        <TextInput
          placeholder="e.g. 7"
          value={targetInput}
          onChangeText={setTargetInput}
          style={[styles.input, isSearching && styles.inputDisabled]}
          editable={!isSearching}
          keyboardType="numeric"
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
                  isSearching && styles.speedBtnDisabled
                ]}
                onPress={() => changeSpeed(spd)}
                disabled={isSearching}
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
            style={[styles.actionBtn, styles.startBtn, isSearching && styles.btnDisabled]} 
            onPress={startSearch}
            disabled={isSearching || !!error}
          >
            <Text style={styles.btnText}>▶️ Start Search</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.actionBtn, styles.resetBtn]} 
            onPress={resetSearch}
          >
            <Text style={styles.btnText}>🔄 Reset</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.actionBtn, styles.randomBtn, isSearching && styles.btnDisabled]} 
            onPress={generateRandomArray}
            disabled={isSearching}
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
            <Text style={styles.sortedNote}>
              {!isArraySorted(parseInputArray(arrayInput)) ? '⚠️ Displaying sorted version of array' : ''}
            </Text>
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
          <Text style={styles.infoTitle}>📖 About Binary Search:</Text>
          <Text style={styles.infoText}>
            • 🔍 Efficient search algorithm for sorted arrays{'\n'}
            • ⏱️ Time Complexity: O(log n) - logarithmic time{'\n'}
            • 💾 Space Complexity: O(1) - constant space{'\n'}
            • 🎯 Divides search range in half with each step{'\n'}
            • 📊 Requires the array to be sorted beforehand
          </Text>
        </View>

        <View style={styles.legendCard}>
          <Text style={styles.legendTitle}>Legend:</Text>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.midBox]} />
            <Text style={styles.legendText}>Middle element being checked</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.rangeBox]} />
            <Text style={styles.legendText}>Current search range (low/high)</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.foundBox]} />
            <Text style={styles.legendText}>Target element found</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, styles.box]} />
            <Text style={styles.legendText}>Outside current search range</Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const PRIMARY_COLOR = '#2563eb';
const SUCCESS_COLOR = '#10b981';
const MID_COLOR = '#f59e0b';
const RANGE_COLOR = '#6b7280';
const LIGHT_BG = '#f9fafb';
const ERROR_COLOR = '#ef4444';

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
    marginVertical: 24,
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
    marginBottom: 8,
    color: '#1f2937',
  },
  inputDisabled: {
    backgroundColor: '#f3f4f6',
    color: '#6b7280',
  },
  inputError: {
    borderColor: ERROR_COLOR,
    backgroundColor: '#fef2f2',
  },
  errorText: {
    color: ERROR_COLOR,
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 12,
    paddingHorizontal: 4,
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
    minWidth: 60,
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
    flexWrap: 'wrap',
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
    borderRadius: 12,
    marginBottom: 20,
    borderWidth: 2,
    borderColor: '#e5e7eb',
    alignItems: 'center',
    padding: 16,
  },
  arrayTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 8,
    color: PRIMARY_COLOR,
    textAlign: 'center',
  },
  sortedNote: {
    fontSize: 12,
    color: ERROR_COLOR,
    fontWeight: '600',
    marginBottom: 16,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  flatListContent: {
    justifyContent: 'center',
    display: 'flex',
    flexDirection: 'row',
    flexWrap: 'wrap',
    alignItems: 'center',
    paddingVertical: 10,
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
  foundBox: {
    backgroundColor: SUCCESS_COLOR,
    borderColor: SUCCESS_COLOR,
    transform: [{ scale: 1.1 }],
  },
  midBox: {
    backgroundColor: MID_COLOR,
    borderColor: MID_COLOR,
    transform: [{ scale: 1.1 }],
  },
  rangeBox: {
    backgroundColor: RANGE_COLOR,
    borderColor: RANGE_COLOR,
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
  labelContainer: {
    position: 'absolute',
    bottom: 4,
    left: 0,
    right: 0,
    alignItems: 'center',
    justifyContent: 'center',
  },
  labelText: {
    fontSize: 10,
    fontWeight: '600',
    color: 'white',
    backgroundColor: 'rgba(0,0,0,0.3)',
    paddingHorizontal: 4,
    borderRadius: 4,
    textAlign: 'center',
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