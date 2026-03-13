jest.mock('react-native-reanimated', () => {
  const Reanimated = require('react-native-reanimated/mock');
  Reanimated.default.call = () => {};
  return Reanimated;
});

// Mock Expo constants/environment
jest.mock('expo-constants', () => ({
  expoConfig: {
    extra: {},
  },
}));

// Mock @expo/vector-icons
jest.mock('@expo/vector-icons', () => ({
  Feather: 'Feather',
  AntDesign: 'AntDesign',
  Ionicons: 'Ionicons',
  MaterialIcons: 'MaterialIcons',
  FontAwesome: 'FontAwesome',
}));

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () =>
  require('@react-native-async-storage/async-storage/jest/async-storage-mock')
);

// Mock react-native-safe-area-context
jest.mock('react-native-safe-area-context', () => {
  const inset = { top: 0, right: 0, bottom: 0, left: 0 };
  return {
    SafeAreaProvider: ({ children }) => children,
    SafeAreaView: ({ children }) => children,
    useSafeAreaInsets: () => inset,
    useSafeAreaFrame: () => ({ x: 0, y: 0, width: 390, height: 844 }),
  };
});

// Mock expo-linear-gradient
jest.mock('expo-linear-gradient', () => ({
  LinearGradient: ({ children }) => children,
}));

// Suppress specific warnings and logs to clean up test output
const originalWarn = console.warn;
const originalError = console.error;
const originalLog = console.log;

console.log = (...args) => {
  // Silent logs during tests
  if (process.env.NODE_ENV === 'test') return;
  originalLog(...args);
};

console.warn = (...args) => {
  const joinedArgs = args.join(' ');
  if (
    joinedArgs.includes('SafeAreaView has been deprecated') || 
    joinedArgs.includes('Consider adding an error boundary') ||
    joinedArgs.includes('An error occurred in the')
  ) {
    return;
  }
  originalWarn(...args);
};

console.error = (...args) => {
  const joinedArgs = args.join(' ');
  if (
    joinedArgs.includes('was not wrapped in act') ||
    joinedArgs.includes('An error occurred in the') ||
    joinedArgs.includes('Consider adding an error boundary')
  ) {
    return;
  }
  originalError(...args);
};
