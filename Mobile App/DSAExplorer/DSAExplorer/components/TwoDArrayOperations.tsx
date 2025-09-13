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

const BOX_SIZE = 60;
const BOX_MARGIN = 8;
const { width } = Dimensions.get('window');
const NUM_COLUMNS = Math.floor(width / (BOX_SIZE + BOX_MARGIN));

type ModalType = 'addRow' | 'updateCell' | 'addColumn' | null;

export function TwoDArrayOperations() {
  const [matrix, setMatrix] = useState<number[][]>([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
  ]);
  const [modalType, setModalType] = useState<ModalType>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [rowIndex, setRowIndex] = useState('');
  const [colIndex, setColIndex] = useState('');
  const [explanation, setExplanation] = useState('3x3 matrix loaded. You can modify it using the operations below.');

  const openModal = (type: ModalType) => {
    setModalType(type);
    setModalVisible(true);
  };

  const closeModal = () => {
    setModalVisible(false);
    setInputValue('');
    setRowIndex('');
    setColIndex('');
  };

  const handleSubmit = () => {
    const value = parseInt(inputValue);
    const row = parseInt(rowIndex);
    const col = parseInt(colIndex);

    switch (modalType) {
      case 'addRow':
        if (!inputValue.trim()) {
          return Alert.alert('Invalid input', 'Enter comma-separated values like "1,2,3"');
        }
        const newRow = inputValue
          .split(',')
          .map((v) => parseInt(v.trim()))
          .filter((n) => !isNaN(n));
        
        if (newRow.length === 0) return Alert.alert('Invalid input', 'No valid numbers entered.');
        
        // If matrix has existing columns, ensure new row has same length
        if (matrix.length > 0 && matrix[0].length !== newRow.length) {
          return Alert.alert('Dimension mismatch', `New row must have ${matrix[0].length} columns`);
        }
        
        setMatrix([...matrix, newRow]);
        setExplanation(`Added new row: [${newRow.join(', ')}]`);
        break;

      case 'addColumn':
        if (isNaN(value)) return Alert.alert('Invalid input', 'Enter a value for the new column.');
        
        const columnMatrix = matrix.map(row => [...row, value]);
        setMatrix(columnMatrix);
        setExplanation(`Added new column with value ${value}`);
        break;

      case 'updateCell':
        if (isNaN(row) || isNaN(col) || isNaN(value)) {
          return Alert.alert('Invalid input', 'Provide valid row, column, and new value.');
        }
        if (row < 0 || row >= matrix.length || col < 0 || col >= matrix[0]?.length) {
          return Alert.alert('Out of bounds', 'Invalid matrix indices.');
        }
        
        const updatedMatrix = matrix.map((r, ri) =>
          ri === row ? r.map((c, ci) => (ci === col ? value : c)) : r
        );
        setMatrix(updatedMatrix);
        setExplanation(`Updated cell [${row}, ${col}] to ${value}`);
        break;
    }

    closeModal();
  };

  const resetMatrix = () => {
    setMatrix([]);
    setExplanation('Matrix cleared. Add rows to build a new matrix.');
  };

  const generateRandomMatrix = () => {
    const rows = Math.floor(Math.random() * 4) + 2; // 2-5 rows
    const cols = Math.floor(Math.random() * 4) + 2; // 2-5 columns
    
    const randomMatrix = Array.from({ length: rows }, () =>
      Array.from({ length: cols }, () => Math.floor(Math.random() * 20) + 1)
    );
    
    setMatrix(randomMatrix);
    setExplanation(`Generated ${rows}x${cols} random matrix`);
  };

  const renderMatrix = () => {
    if (matrix.length === 0) {
      return (
        <View style={styles.emptyState}>
          <Text style={styles.emptyText}>Matrix is empty</Text>
          <Text style={styles.emptySubtext}>Add rows to get started</Text>
        </View>
      );
    }

    return (
      <View style={styles.matrix}>
        {matrix.map((row, rIdx) => (
          <View key={rIdx} style={styles.row}>
            {row.map((cell, cIdx) => (
              <View key={`${rIdx}-${cIdx}`} style={styles.box}>
                <Text style={styles.boxText}>{cell}</Text>
                <Text style={styles.coordText}>{rIdx},{cIdx}</Text>
              </View>
            ))}
          </View>
        ))}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={{ flexGrow: 1 }}>
        <View style={styles.container}>
          <Text style={styles.header}>🧮 2D Array Operations</Text>
          <Text style={styles.explanation}>{explanation}</Text>

          {/* Matrix Info */}
          <View style={styles.infoCard}>
            <Text style={styles.infoTitle}>Matrix Information</Text>
            <Text style={styles.infoText}>
              • Dimensions: {matrix.length} × {matrix[0]?.length || 0}{'\n'}
              • Total Elements: {matrix.length * (matrix[0]?.length || 0)}{'\n'}
              • Row Indexes: 0 to {matrix.length - 1}{'\n'}
              • Column Indexes: 0 to {(matrix[0]?.length || 1) - 1}
            </Text>
          </View>
          <View style={styles.buttonRow}>
          {/* Operation Buttons */}
          <TouchableOpacity style={styles.button} onPress={() => openModal('addRow')}>
            <Text style={styles.buttonText}>Add Row</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.button} onPress={() => openModal('addColumn')}>
            <Text style={styles.buttonText}>Add Column</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.button} onPress={() => openModal('updateCell')}>
            <Text style={styles.buttonText}>Update Cell</Text>
          </TouchableOpacity>

          <TouchableOpacity style={[styles.button, styles.randomButton]} onPress={generateRandomMatrix}>
            <Text style={styles.buttonText}>Generate Random Matrix</Text>
          </TouchableOpacity>

          <TouchableOpacity style={[styles.button, styles.resetButton]} onPress={resetMatrix}>
            <Text style={styles.buttonText}>Clear Matrix</Text>
          </TouchableOpacity>
          </View>
          {/* Matrix Display */}
          <View style={styles.matrixContainer}>
            <Text style={styles.matrixTitle}>Matrix Visualization:</Text>
            {renderMatrix()}
          </View>

          {/* Legend */}
          <View style={styles.legendCard}>
            <Text style={styles.legendTitle}>How to Use:</Text>
            <Text style={styles.legendText}>
              • Add Row: Append a new row with comma-separated values{'\n'}
              • Add Column: Append a new column with the same value in all rows{'\n'}
              • Update Cell: Change a specific cell's value{'\n'}
              • Coordinates show as row,column (e.g., "0,1")
            </Text>
          </View>

          {/* Modal for Input */}
          <Modal visible={modalVisible} animationType="slide" transparent>
            <View style={styles.modalOverlay}>
              <View style={styles.modalContainer}>
                <Text style={styles.modalTitle}>
                  {modalType === 'addRow' ? 'ADD ROW' : 
                   modalType === 'addColumn' ? 'ADD COLUMN' : 'UPDATE CELL'}
                </Text>

                {modalType === 'addRow' ? (
                  <>
                    <Text style={styles.modalHint}>
                      {matrix.length > 0 ? `Enter ${matrix[0].length} comma-separated values` : 'Enter comma-separated values'}
                    </Text>
                    <TextInput
                      placeholder='e.g., 1,2,3,4'
                      value={inputValue}
                      onChangeText={setInputValue}
                      style={styles.modalInput}
                      keyboardType="numbers-and-punctuation"
                    />
                  </>
                ) : modalType === 'addColumn' ? (
                  <TextInput
                    placeholder="Value for new column"
                    value={inputValue}
                    onChangeText={setInputValue}
                    keyboardType="numeric"
                    style={styles.modalInput}
                  />
                ) : (
                  <>
                    <TextInput
                      placeholder="Row Index"
                      value={rowIndex}
                      onChangeText={setRowIndex}
                      keyboardType="numeric"
                      style={styles.modalInput}
                    />
                    <TextInput
                      placeholder="Column Index"
                      value={colIndex}
                      onChangeText={setColIndex}
                      keyboardType="numeric"
                      style={styles.modalInput}
                    />
                    <TextInput
                      placeholder="New Value"
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

const PRIMARY_COLOR = '#2563eb';
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
  header: {
    fontSize: 28,
    fontWeight: '700',
    color: PRIMARY_COLOR,
    marginBottom: 16,
    textAlign: 'center',
  },
  explanation: {
    fontSize: 16,
    color: '#374151',
    marginBottom: 20,
    textAlign: 'center',
    fontStyle: 'italic',
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
    marginBottom: 8,
    color: PRIMARY_COLOR,
  },
  infoText: {
    fontSize: 14,
    lineHeight: 20,
    color: '#374151',
  },
  button: {
    backgroundColor: PRIMARY_COLOR,
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 16,
    marginBottom: 12,
    alignItems: 'center',
    ...(Platform.OS === "web" && {
      width: '20%',
    })
  },
  resetButton: {
    backgroundColor: '#ef4444',
  },
  randomButton: {
    backgroundColor: '#8b5cf6',
  },
  buttonRow: {
    ...(Platform.OS === "web" && {
      flexDirection: 'row',
      justifyContent: 'space-between',
      width: '100%',
      gap: 4,
    }),
    paddingVertical:10
  },
  buttonText: {
    color: 'white',
    fontWeight: '700',
    fontSize: 16,
  },
  matrixContainer: {
    marginTop: 24,
    marginBottom: 16,
    alignItems: 'center',
  },
  matrixTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 16,
    color: PRIMARY_COLOR,
    textAlign: 'center',
  },
  matrix: {
    alignItems: 'center',
  },
  row: {
    flexDirection: 'row',
    marginBottom: BOX_MARGIN,
  },
  box: {
    width: BOX_SIZE,
    height: BOX_SIZE,
    backgroundColor: 'white',
    marginHorizontal: BOX_MARGIN / 2,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: PRIMARY_COLOR,
    position: 'relative',
  },
  boxText: {
    fontSize: 18,
    fontWeight: '700',
    color: PRIMARY_COLOR,
  },
  coordText: {
    position: 'absolute',
    bottom: 4,
    fontSize: 10,
    color: '#6b7280',
  },
  emptyState: {
    padding: 40,
    alignItems: 'center',
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
  legendText: {
    fontSize: 14,
    lineHeight: 20,
    color: '#374151',
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
    width: Platform.OS === "web" ? '50%' : '85%',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: PRIMARY_COLOR,
    marginBottom: 16,
  },
  modalHint: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 8,
    textAlign: 'center',
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
  },
  modalButton: {
    flex: 1,
    backgroundColor: PRIMARY_COLOR,
    borderRadius: 12,
    paddingVertical: 14,
    marginRight: 8,
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: '#6b7280',
    marginRight: 0,
    marginLeft: 8,
  },
});