import React, { useState, useEffect } from 'react';
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
  Platform,
} from 'react-native';

export function StringManipulations() {
  const [inputText, setInputText] = useState('');
  const [concatenateText, setConcatenateText] = useState('');
  const [result, setResult] = useState<string | null>(null);
  const [operation, setOperation] = useState<string | null>(null);
  const [animatedResult, setAnimatedResult] = useState<string[]>([]);
  const [isAnimating, setIsAnimating] = useState(false);
  const [inputLetters, setInputLetters] = useState<string[]>([]);
  const [concatLetters, setConcatLetters] = useState<string[]>([]);

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
    },
    concatenate: (str1: string, str2: string): string => {
      return str1 + str2;
    }
  };

  // Update input letters when text changes
  useEffect(() => {
    setInputLetters(inputText.split(''));
  }, [inputText]);

  // Update concat letters when text changes
  useEffect(() => {
    setConcatLetters(concatenateText.split(''));
  }, [concatenateText]);

  // Animate concatenation letter by letter
  useEffect(() => {
    if (operation === 'concatenate' && result && isAnimating) {
      const fullText = result;
      setAnimatedResult([]);
      
      let currentIndex = -1;
      const interval = setInterval(() => {
        if (currentIndex < fullText.length-1) {
          setAnimatedResult(prev => [...prev, fullText[currentIndex]]);
          currentIndex++;
        } else {
          clearInterval(interval);
          setIsAnimating(false);
        }
      }, 100);
      
      return () => clearInterval(interval);
    } else if (result && operation !== 'concatenate') {
      // Only set animated result for operations that should show character boxes
      const shouldShowBoxes = ['reverse', 'uppercase', 'lowercase', 'titlecase'].includes(operation || '');
      if (shouldShowBoxes) {
        setAnimatedResult(result.split(''));
      } else {
        setAnimatedResult([]);
      }
    }
  }, [result, operation, isAnimating]);

  const handleOperation = (op: string) => {
    if (inputText.trim() === '') {
      Alert.alert('Input Required', 'Please enter some text to perform operations');
      return;
    }
    
    setOperation(op);
    console.log('Operation:', op);
    if (op === 'concatenate') {
      if (concatenateText.trim() === '') {
        Alert.alert('Second Text Required', 'Please enter text to concatenate');
        return;
      }
      setIsAnimating(true);
      setResult(stringOperations.concatenate(inputText, concatenateText));
    } else {
      setIsAnimating(false);
      const operationResult = stringOperations[op as keyof typeof stringOperations](inputText);
      setResult(operationResult);
      
      // Only animate for operations that should show character boxes
      const shouldShowBoxes = ['reverse', 'uppercase', 'lowercase', 'titlecase'].includes(op);
      if (shouldShowBoxes) {
        setAnimatedResult(operationResult.split(''));
      } else {
        setAnimatedResult([]);
      }
    }
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

  const renderLetterBoxes = (letters: string[], title: string) => (
    <View style={styles.letterSection}>
      <Text style={styles.letterSectionTitle}>{title}</Text>
      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={true}
        style={styles.letterScrollView}
      >
        <View style={styles.letterContainer}>
          {letters.map((letter, index) => (
            <View key={index} style={styles.letterColumn}>
              <Text style={styles.indexText}>{index}</Text>
              <View style={styles.letterBox}>
                <Text style={styles.letterText}>{letter}</Text>
              </View>
            </View>
          ))}
          {/* Add null terminator box at the end */}
          {letters.length > 0 && (
            <View style={styles.letterColumn}>
              <Text style={styles.indexText}>{letters.length}</Text>
              <View style={styles.nullTerminatorBox}>
                <Text style={styles.nullTerminatorText}>/0</Text>
              </View>
            </View>
          )}
          {letters.length === 0 && (
            <View style={styles.placeholderBox}>
              <Text style={styles.placeholderText}>Type to add letters</Text>
            </View>
          )}
        </View>
      </ScrollView>
    </View>
  );

  const renderResult = () => {
    if (operation === 'concatenate') {
      return (
        <View style={styles.animationContainer}>
          <View style={styles.animationStep}>
            {renderLetterBoxes(inputLetters, "First Text")}
            <Text style={styles.plusSign}>+</Text>
            {renderLetterBoxes(concatLetters, "Second Text")}
            <Text style={styles.equalsSign}>=</Text>
          </View>
          
          <View style={styles.animationStep}>
            <Text style={styles.animationTitle}>Concatenated Result:</Text>
            <ScrollView 
              horizontal 
              showsHorizontalScrollIndicator={true}
              style={styles.letterScrollView}
            >
              <View style={styles.letterContainer}>
                {animatedResult.map((letter, index) => (
                  <View key={index} style={styles.letterColumn}>
                    <Text style={styles.indexText}>{index}</Text>
                    <View style={styles.resultLetterBox}>
                      <Text style={styles.letterText}>{letter}</Text>
                    </View>
                  </View>
                ))}
                {/* Add null terminator box at the end of the result */}
                {!isAnimating && animatedResult.length > 0 && (
                  <View style={styles.letterColumn}>
                    <Text style={styles.indexText}>{animatedResult.length}</Text>
                    <View style={styles.nullTerminatorBox}>
                      <Text style={styles.nullTerminatorText}>/0</Text>
                    </View>
                  </View>
                )}
                {isAnimating && (
                  <View style={styles.letterColumn}>
                    <Text style={styles.indexText}>{animatedResult.length}</Text>
                    <View style={styles.cursorBox}>
                      <Text style={styles.cursorText}>|</Text>
                    </View>
                  </View>
                )}
              </View>
            </ScrollView>
          </View>
        </View>
      );
    } else if (result && animatedResult.length > 0) {
      // Show character boxes only for specific operations
      const shouldShowBoxes = ['reverse', 'uppercase', 'lowercase', 'titlecase'].includes(operation || '');
      if (shouldShowBoxes) {
        return (
          <View style={styles.animationContainer}>
            <Text style={styles.animationTitle}>Result:</Text>
            <ScrollView 
              horizontal 
              showsHorizontalScrollIndicator={true}
              style={styles.letterScrollView}
            >
              <View style={styles.letterContainer}>
                {animatedResult.map((letter, index) => (
                  <View key={index} style={styles.letterColumn}>
                    <Text style={styles.indexText}>{index}</Text>
                    <View style={styles.resultLetterBox}>
                      <Text style={styles.letterText}>{letter}</Text>
                    </View>
                  </View>
                ))}
                {/* Add null terminator box at the end of the result */}
                <View style={styles.letterColumn}>
                  <Text style={styles.indexText}>{animatedResult.length}</Text>
                  <View style={styles.nullTerminatorBox}>
                    <Text style={styles.nullTerminatorText}>/0</Text>
                  </View>
                </View>
              </View>
            </ScrollView>
          </View>
        );
      } else {
        // For operations that shouldn't show boxes, display simple text
        return (
          <View style={styles.simpleResultContainer}>
            <Text style={styles.simpleResultText}>{result}</Text>
          </View>
        );
      }
    } else if (result) {
      // Fallback for operations that don't have animated result but should show text
      return (
        <View style={styles.simpleResultContainer}>
          <Text style={styles.simpleResultText}>{result}</Text>
        </View>
      );
    }
    return null;
  };

    const clearAll = () => {
      setInputText('');
      setConcatenateText('');
      setResult(null);
      setOperation(null);
      setAnimatedResult([]);
      setIsAnimating(false);
      setInputLetters([]);
      setConcatLetters([]);
    };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>🔤 String Manipulation</Text>
        </View>
        
        <Text style={styles.subtitle}>Transform and analyze your text</Text>

        <View style={styles.inputContainer}>
          <Text style={styles.label}>Enter your text:</Text>
          <TextInput
            style={styles.input}
            placeholder="Type or paste your text here..."
            value={inputText}
            onChangeText={setInputText}
            multiline
            numberOfLines={2}
          />
          {renderLetterBoxes(inputLetters, "Your Text (Character by Character)")}
        </View>

        {operation === 'concatenate' && (
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Text to concatenate:</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter text to add to the end..."
              value={concatenateText}
              onChangeText={setConcatenateText}
              multiline
              numberOfLines={2}
            />
            {renderLetterBoxes(concatLetters, "Text to Concatenate")}
          </View>
        )}

        <View style={styles.operationsGrid}>
          <OperationButton title="Reverse" op="reverse" icon="🔄" />
          <OperationButton title="Uppercase" op="uppercase" icon="🔠" />
          <OperationButton title="Lowercase" op="lowercase" icon="🔡" />
          <OperationButton title="Title Case" op="titlecase" icon="🏷️" />
          <OperationButton title="Concatenate" op="concatenate" icon="➕" />
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
              {renderResult()}
            </View>
          </View>
        )}
        
        <View style={styles.clearButtonContainer}>
          <TouchableOpacity 
            style={[styles.button, styles.clearButton]} 
            onPress={clearAll}
            disabled={!inputText && !result && !concatenateText}
          >
            <Text style={styles.buttonText}>🗑️ Clear All</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>💡 Tips:</Text>
          <Text style={styles.infoText}>
            • Type to see each character appear in its own box{'\n'}
            • Use Concatenate to join two texts together visually{'\n'}
            • Watch the animation as characters combine{'\n'}
            • /0 represents the null terminator (end of string){'\n'}
            • Transform operations show character boxes, analysis shows text{'\n'}
            • Index numbers show the position of each character (0-based)
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  title: {
    fontSize: 32,
    fontWeight: '800',
    color: PRIMARY_COLOR,
    flex: 1,
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    marginBottom: 32,
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
    minHeight: 80,
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
    width: Platform.OS === "web" ? '22%' : '48%',
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
    marginBottom: 8,
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
    padding: 10,
    borderLeftWidth: 4,
    borderLeftColor: PRIMARY_COLOR,
    minHeight: 60,
  },
  animationContainer: {
    padding: 10,
  },
  animationStep: {
    marginBottom: 20,
    alignItems: 'center',
  },
  animationTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: PRIMARY_COLOR,
    marginBottom: 10,
  },
  letterSection: {
    marginBottom: 15,
  },
  letterSectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#4b5563',
    marginBottom: 8,
    textAlign: 'center',
  },
  letterScrollView: {
    maxHeight: 70,
  },
  letterContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    padding: 5,
  },
  letterColumn: {
    alignItems: 'center',
    margin: 2,
  },
  indexText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#6b7280',
    marginBottom: 2,
    minHeight: 12,
  },
  letterBox: {
    width: 40,
    height: 40,
    backgroundColor: '#dbeafe',
    borderRadius: 8,
    borderWidth: 2,
    borderColor: PRIMARY_COLOR,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 2,
    shadowOffset: { width: 0, height: 1 },
  },
  resultLetterBox: {
    width: 40,
    height: 40,
    backgroundColor: 'white',
    borderRadius: 8,
    borderWidth: 2,
    borderColor: PRIMARY_COLOR,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 2,
    shadowOffset: { width: 0, height: 1 },
  },
  nullTerminatorBox: {
    width: 40,
    height: 40,
    backgroundColor: '#fef3c7',
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#d97706',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 2,
    shadowOffset: { width: 0, height: 1 },
  },
  nullTerminatorText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#d97706',
  },
  placeholderBox: {
    width: 180,
    height: 40,
    backgroundColor: '#f3f4f6',
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#d1d5db',
    justifyContent: 'center',
    alignItems: 'center',
    margin: 2,
  },
  placeholderText: {
    fontSize: 12,
    color: '#9ca3af',
    fontStyle: 'italic',
  },
  letterText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: PRIMARY_COLOR,
  },
  plusSign: {
    fontSize: 24,
    fontWeight: 'bold',
    color: PRIMARY_COLOR,
    marginHorizontal: 10,
    marginTop: 20,
  },
  equalsSign: {
    fontSize: 24,
    fontWeight: 'bold',
    color: PRIMARY_COLOR,
    marginHorizontal: 10,
    marginTop: 20,
  },
  cursorBox: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  cursorText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: PRIMARY_COLOR,
  },
  simpleResultContainer: {
    padding: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  simpleResultText: {
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
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-around',
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