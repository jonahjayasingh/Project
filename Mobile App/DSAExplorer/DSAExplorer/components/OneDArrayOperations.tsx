import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  Alert,
  StatusBar,
  Dimensions,
  TouchableOpacity,
  Modal,
  TextInput,
  ScrollView,
  Platform,
} from 'react-native';
import { FontAwesome } from '@expo/vector-icons';

const BOX_SIZE = 60;
const BOX_MARGIN = 8;
const { width } = Dimensions.get('window');
const NUM_COLUMNS = Math.floor(width / (BOX_SIZE + BOX_MARGIN));

type ModalType = 'add' | 'update' | 'search' | 'concat' | null;

export function OneDArrayOperations() {
  const [array, setArray] = useState<number[]>([]);
  const [modalType, setModalType] = useState<ModalType>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [indexValue, setIndexValue] = useState('');
  const [highlightIndex, setHighlightIndex] = useState<number | null>(null);
  const [explanation, setExplanation] = useState('Array is empty. Start by adding elements.');

  const openModal = (type: ModalType) => {
    setModalType(type);
    setModalVisible(true);
  };

  const closeModal = () => {
    setModalVisible(false);
    setInputValue('');
    setIndexValue('');
  };

  const handleSubmit = () => {
    const value = parseInt(inputValue);
    const idx = parseInt(indexValue);

    switch (modalType) {
      case 'add':
        if (!inputValue.trim()) {
          return Alert.alert('Invalid input', 'Enter comma-separated values like "1,2,3"');
        }
        const newElements = inputValue
          .split(',')
          .map((v) => parseInt(v.trim()))
          .filter((n) => !isNaN(n));
        if (newElements.length === 0) return Alert.alert('Invalid input', 'No valid numbers entered.');
        setArray([...array, ...newElements]);
        setExplanation(`Added elements: [${newElements.join(', ')}]`);
        break;

      case 'update':
        if (isNaN(idx) || isNaN(value)) {
          return Alert.alert('Invalid input', 'Enter valid index and value.');
        }
        if (idx < 0 || idx >= array.length) {
          return Alert.alert('Out of bounds', 'Index out of range.');
        }
        const updatedArray = array.map((el, i) => (i === idx ? value : el));
        setArray(updatedArray);
        setExplanation(`Updated index ${idx} to ${value}`);
        break;

      case 'search':
        if (isNaN(value)) {
          return Alert.alert('Invalid input', 'Enter a number to search.');
        }
        const foundIndex = array.indexOf(value);
        if (foundIndex !== -1) {
          setHighlightIndex(foundIndex);
          setExplanation(`Found ${value} at index ${foundIndex}`);
          Alert.alert('Found', `Value found at index ${foundIndex}`);
        } else {
          setHighlightIndex(null);
          setExplanation(`${value} not found in array`);
          Alert.alert('Not Found', 'Value not found in array');
        }
        break;

      case 'concat':
        if (!inputValue.trim()) {
          return Alert.alert('Invalid input', 'Enter comma-separated values like "1,2,3"');
        }
        const concatElements = inputValue
          .split(',')
          .map((v) => parseInt(v.trim()))
          .filter((n) => !isNaN(n));
        if (concatElements.length === 0) return Alert.alert('Invalid input', 'No valid numbers entered.');
        setArray([...array, ...concatElements]);
        setExplanation(`Concatenated elements: [${concatElements.join(', ')}]`);
        break;
    }

    closeModal();
  };

  const resetArray = () => {
    setArray([]);
    setHighlightIndex(null);
    setExplanation('Array reset. Start adding elements again.');
  };

  const generateRandomArray = () => {
    const randomArray = Array.from({ length: 10 }, () => 
      Math.floor(Math.random() * 20) + 1
    );
    setArray(randomArray);
    setHighlightIndex(null);
    setExplanation(`Generated random array with ${randomArray.length} elements`);
  };

  const renderArray = () => (
    <View style={styles.row}>
      {array.map((cell, idx) => {
        const isHighlighted = highlightIndex === idx;
        return (
          <View key={idx} style={[styles.box, isHighlighted && styles.highlightBox]}>
            <Text style={[styles.boxText, isHighlighted && { color: 'white' }]}>{cell}</Text>
            <Text style={styles.indexText}>{idx}</Text>
          </View>
        );
      })}
    </View>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={{ flexGrow: 1 }}>
        <View style={styles.container}>
          <View style={styles.headerRow}>
            <Text style={styles.header}>🧮 1D Array Operations</Text>
          </View>

          <View style={styles.buttonRow}>
            <TouchableOpacity style={styles.button} onPress={() => openModal('add')}>
              <FontAwesome name="plus" size={16} color="white" />
              <Text style={styles.buttonText}> Add</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.button} onPress={() => openModal('update')}>
              <FontAwesome name="pencil" size={16} color="white" />
              <Text style={styles.buttonText}> Update</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.button} onPress={() => openModal('search')}>
              <FontAwesome name="search" size={16} color="white" />
              <Text style={styles.buttonText}> Search</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.button} onPress={() => openModal('concat')}>
              <FontAwesome name="link" size={16} color="white" />
              <Text style={styles.buttonText}> Concat</Text>
            </TouchableOpacity>

            <TouchableOpacity style={[styles.button, styles.randomButton]} onPress={generateRandomArray}>
              <FontAwesome name="random" size={16} color="white" />
              <Text style={styles.buttonText}> Random</Text>
            </TouchableOpacity>

            <TouchableOpacity style={[styles.button, styles.resetButton]} onPress={resetArray}>
              <FontAwesome name="refresh" size={16} color="white" />
              <Text style={styles.buttonText}> Reset</Text>
            </TouchableOpacity>
          </View>

          {array.length > 0 && (
            <View style={styles.arrayContainer}>
              <Text style={styles.arrayTitle}>Array Visualization:</Text>
              {renderArray()}
            </View>
          )}

          {/* Info Card */}
          <View style={styles.infoCard}>
            <Text style={styles.infoTitle}>ℹ️ Array Information:</Text>
            <Text style={styles.infoText}>
              • Array Length: {array.length}{'\n'}
              • Array Type: 1-dimensional{'\n'}
              • Index Range: 0 to {array.length - 1}{'\n'}
              • Operations: Add, Update, Search, Concat
            </Text>
          </View>

          {/* Legend */}
          <View style={styles.legendCard}>
            <Text style={styles.legendTitle}>Legend:</Text>
            <View style={styles.legendItem}>
              <View style={[styles.legendColor, styles.highlightBox]} />
              <Text style={styles.legendText}>Found element (search result)</Text>
            </View>
            <View style={styles.legendItem}>
              <View style={[styles.legendColor, styles.box]} />
              <Text style={styles.legendText}>Regular array element</Text>
            </View>
          </View>

          {/* Modal for Input */}
          <Modal visible={modalVisible} animationType="slide" transparent>
            <View style={styles.modalOverlay}>
              <View style={styles.modalContainer}>
                <Text style={styles.modalTitle}>{modalType?.toUpperCase()}</Text>

                {modalType === 'add' || modalType === 'concat' ? (
                  <TextInput
                    placeholder='Comma-separated elements (e.g. 1,2,3)'
                    value={inputValue}
                    onChangeText={setInputValue}
                    style={styles.modalInput}
                    keyboardType="default"
                    autoCapitalize="none"
                  />
                ) : (
                  <>
                    {(modalType === 'update') && (
                      <TextInput
                        placeholder="Index"
                        value={indexValue}
                        onChangeText={setIndexValue}
                        keyboardType="numeric"
                        style={styles.modalInput}
                      />
                    )}
                    <TextInput
                      placeholder={modalType === 'search' ? 'Value to search' : 'New Value'}
                      value={inputValue}
                      onChangeText={setInputValue}
                      keyboardType="numeric"
                      style={styles.modalInput}
                    />
                  </>
                )}

                <View style={styles.modalButtonRow}>
                  <TouchableOpacity style={styles.modalButton} onPress={handleSubmit}>
                    <Text style={styles.buttonText}>Submit</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={[styles.modalButton, styles.cancelButton]} onPress={closeModal}>
                    <Text style={styles.buttonText}>Cancel</Text>
                  </TouchableOpacity>
                </View>
              </View>
            </View>
          </Modal>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

// Styles remain unchanged from your original code

const PRIMARY_COLOR = '#2563eb';
const HIGHLIGHT_COLOR = '#10b981';
const LIGHT_BG = '#f9fafb';

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: LIGHT_BG,
    paddingTop: StatusBar.currentHeight,
  },
  container: {
    flex: 1,
    padding: 24,
    paddingBottom: 100,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  header: {
    fontSize: 28,
    fontWeight: '700',
    color: PRIMARY_COLOR,
  },
  explanation: {
    fontSize: 16,
    color: '#374151',
    marginBottom: 20,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  buttonRow: {
    flexDirection: Platform.OS === "web" ? 'row' : 'column',
    flexWrap: Platform.OS === "web" ? 'wrap' : 'nowrap',
    justifyContent: 'space-between',
    gap: 8,
    marginBottom: 16,
  },
  button: {
    backgroundColor: PRIMARY_COLOR,
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 16,
    alignItems: 'center',
    minWidth: Platform.OS === "web" ? 100 : '100%',
    flex: Platform.OS === "web" ? 1 : 0,
    marginBottom: Platform.OS === "web" ? 0 : 8,
    flexDirection: 'row',
    justifyContent: 'center',
  },
  resetButton: {
    backgroundColor: '#ef4444',
  },
  randomButton: {
    backgroundColor: '#8b5cf6',
  },
  buttonText: {
    color: 'white',
    fontWeight: '700',
    fontSize: 14,
  },
  arrayContainer: {
    marginTop: 24,
    marginBottom: 16,
    alignItems: 'center',
  },
  arrayTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 16,
    color: PRIMARY_COLOR,
    textAlign: 'center',
  },
  row: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    marginBottom: BOX_MARGIN / 2,
  },
  box: {
    width: BOX_SIZE,
    height: BOX_SIZE,
    backgroundColor: 'white',
    marginHorizontal: BOX_MARGIN / 2,
    marginVertical: BOX_MARGIN / 2,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: PRIMARY_COLOR,
    position: 'relative',
  },
  highlightBox: {
    backgroundColor: HIGHLIGHT_COLOR,
    borderColor: HIGHLIGHT_COLOR,
  },
  boxText: {
    fontSize: 18,
    fontWeight: '700',
    color: PRIMARY_COLOR,
  },
  indexText: {
    position: 'absolute',
    top: 4,
    fontSize: 10,
    fontWeight: '600',
    color: '#6b7280',
  },
  infoCard: {
    backgroundColor: '#f0f9ff',
    padding: 16,
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
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 1,
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

  // Modal Styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContainer: {
    backgroundColor: 'white',
    width: Platform.OS === "web" ? '40%' : '85%',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    maxWidth: 400,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: PRIMARY_COLOR,
    marginBottom: 16,
  },
  modalInput: {
    width: '100%',
    height: 50,
    borderWidth: 1.5,
    borderColor: '#d1d5db',
    borderRadius: 12,
    paddingHorizontal: 16,
    fontSize: 16,
    backgroundColor: 'white',
    color: '#1f2937',
    marginBottom: 12,
  },
  modalButtonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    gap: 12,
  },
  modalButton: {
    flex: 1,
    backgroundColor: PRIMARY_COLOR,
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: '#6b7280',
  },
});