import React, { useState } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  StatusBar,
  Platform
} from 'react-native';

export function StringManipulations() {
  const [inputText, setInputText] = useState('');
  const [result, setResult] = useState<string | null>(null);
  const [operation, setOperation] = useState<string | null>(null);

  const stringOperations = {
    reverse: (str: string): string => {
      return str.split('').reverse().join('');
    },
    uppercase: (str: string): string => {
      return str.toUpperCase();
    },
    lowercase: (str: string): string => {
      return str.toLowerCase();
    },
    palindrome: (str: string): string => {
      const cleaned = str.replace(/[^A-Za-z0-9]/g, '').toLowerCase();
      return cleaned === cleaned.split('').reverse().join('') 
        ? 'Yes, it is a palindrome!' 
        : 'No, not a palindrome';
    },
    vowels: (str: string): string => {
      const vowels = str.match(/[aeiouAEIOU]/g);
      return `Vowel count: ${vowels ? vowels.length : 0}`;
    },
    words: (str: string): string => {
      const words = str.trim().split(/\s+/).filter(word => word.length > 0);
      return `Word count: ${words.length}`;
    },
    characters: (str: string): string => {
      return `Character count: ${str.length}`;
    },
    titlecase: (str: string): string => {
      return str.replace(/\w\S*/g, (txt) => {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
      });
    }
  };

  const handleOperation = (op: string) => {
    if (inputText.trim() === '') {
      Alert.alert('Input Required', 'Please enter some text to perform operations');
      return;
    }
    
    setOperation(op);
    setResult(stringOperations[op as keyof typeof stringOperations](inputText));
  };

  const clearAll = () => {
    setInputText('');
    setResult(null);
    setOperation(null);
  };

  const OperationButton = ({ title, op, icon }: { title: string, op: string, icon: string }) => (
    <TouchableOpacity 
      style={[
        styles.operationButton, 
        operation === op && styles.activeOperation
      ]} 
      onPress={() => handleOperation(op)}
    >
      <Text style={styles.operationIcon}>{icon}</Text>
      <Text style={styles.operationText}>{title}</Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>🔤 String Manipulation</Text>
        <Text style={styles.subtitle}>Transform and analyze your text</Text>

        <View style={styles.inputContainer}>
          <Text style={styles.label}>Enter your text:</Text>
          <TextInput
            style={styles.input}
            placeholder="Type or paste your text here..."
            value={inputText}
            onChangeText={setInputText}
            multiline
            numberOfLines={4}
          />
          <Text style={styles.charCount}>
            {inputText.length} character{inputText.length !== 1 ? 's' : ''}
          </Text>
        </View>

        <View style={styles.operationsGrid}>
          <OperationButton title="Reverse" op="reverse" icon="🔄" />
          <OperationButton title="Uppercase" op="uppercase" icon="🔠" />
          <OperationButton title="Lowercase" op="lowercase" icon="🔡" />
          <OperationButton title="Title Case" op="titlecase" icon="🏷️" />
          <OperationButton title="Palindrome" op="palindrome" icon="📖" />
          <OperationButton title="Count Vowels" op="vowels" icon="🔊" />
          <OperationButton title="Count Words" op="words" icon="📝" />
          <OperationButton title="Count Chars" op="characters" icon="🔢" />
        </View>

        {result !== null && (
          <View style={styles.resultContainer}>
            <Text style={styles.resultLabel}>
              {operation ? operation.charAt(0).toUpperCase() + operation.slice(1) : 'Result'}:
            </Text>
            <View style={styles.resultBox}>
              <Text style={styles.resultText}>{result}</Text>
            </View>
          </View>
        )}
        <View style={styles.clearButtonContainer}>
          <TouchableOpacity 
            style={[styles.button, styles.clearButton]} 
            onPress={clearAll}
            disabled={!inputText && !result}
          >
            <Text style={styles.buttonText}>🗑️ Clear All</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>💡 Tips:</Text>
          <Text style={styles.infoText}>
            • Use Reverse to flip your text{'\n'}
            • Palindrome check ignores spaces and punctuation{'\n'}
            • Title Case capitalizes each word{'\n'}
            • Word count ignores extra spaces
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const PRIMARY_COLOR = '#2563eb';
const SECONDARY_COLOR = '#8b5cf6';
const SUCCESS_COLOR = '#10b981';
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
  title: {
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
    fontStyle: 'italic',
  },
  inputContainer: {
    marginBottom: 24,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  input: {
    minHeight: 120,
    borderColor: '#d1d5db',
    borderWidth: 2,
    borderRadius: 16,
    padding: 16,
    fontSize: 16,
    backgroundColor: 'white',
    color: '#1f2937',
    textAlignVertical: 'top',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
  },
  charCount: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'right',
    marginTop: 8,
  },
  operationsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-evenly',
    marginBottom: 24,
    gap: Platform.OS === "web" ? 4 : 6,

  },
  operationButton: {
    width: Platform.OS === "web" ? '20%' : '100%',
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#e5e7eb',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },

  },
  activeOperation: {
    borderColor: PRIMARY_COLOR,
    backgroundColor: '#eff6ff',
    transform: [{ scale: 1.02 }],
  },
  operationIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  operationText: {
    fontSize: 14,
    fontWeight: '600',
    color: PRIMARY_COLOR,
    textAlign: 'center',
  },
  resultContainer: {
    marginBottom: 24,
  },
  resultLabel: {
    fontSize: 18,
    fontWeight: '700',
    color: PRIMARY_COLOR,
    marginBottom: 12,
  },
  resultBox: {
    backgroundColor: '#e0e7ff',
    borderRadius: 16,
    padding: 20,
    borderLeftWidth: 4,
    borderLeftColor: PRIMARY_COLOR,
  },
  resultText: {
    fontSize: 18,
    fontWeight: '600',
    color: PRIMARY_COLOR,
    textAlign: 'center',
  },
  button: {
    backgroundColor: PRIMARY_COLOR,
    borderRadius: 16,
    paddingVertical: 16,
    paddingHorizontal: 24,
    alignItems: 'center',
    marginBottom: 24,
    shadowColor: PRIMARY_COLOR,
    shadowOpacity: 0.3,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 4 },
  },
  clearButtonContainer: {
    width: '100%',
    alignItems: 'center',
  },
  clearButton: {
    backgroundColor: '#6b7280',
    ...(Platform.OS === 'web' && {
      display:'flex',
      alignItems:'center',
      justifyContent:'space-around',
      width: '20%',
    })
  },
  buttonText: {
    color: 'white',
    fontWeight: '700',
    fontSize: 16,
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