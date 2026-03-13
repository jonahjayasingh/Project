module.exports = {
  preset: 'react-native',
  setupFilesAfterEnv: [
    '@testing-library/jest-native/extend-expect',
    './jest.setup.js'
  ],
  transformIgnorePatterns: [
    'node_modules/(?!(jest-)?react-native|@react-native(-community)?|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|@unimodules/.*|unimodules|sentry-expo|native-base|react-native-svg|nativewind|@testing-library|react-native-reanimated|expo-linear-gradient|expo-status-bar|@expo/vector-icons)',
  ],
  moduleNameMapper: {
    '\\.css$': 'identity-obj-proxy',
    '^AuthContext$': '<rootDir>/AuthContext',
  },
  moduleDirectories: ['node_modules', '<rootDir>'],
};