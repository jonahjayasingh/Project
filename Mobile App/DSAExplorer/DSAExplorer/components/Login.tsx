import React, { useState } from 'react';
import {
  Text,
  View,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { Feather } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useAuth } from '../AuthContext';

type RootStackParamList = {
  Home: undefined;
  Login: undefined;
  Register: undefined;
  Main: undefined;
};

type LoginScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'Login'
>;

// API base URL - adjust to your backend URL
const API_BASE_URL =
  Platform.OS === 'web'
    ? 'http://127.0.0.1:8000'
    : 'http://10.0.2.2:8000';

export const Login = () => {
  const navigation = useNavigation<LoginScreenNavigationProp>();
  const { login } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please enter email and password');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();

      // Store tokens for later use
      await AsyncStorage.setItem('accessToken', data.access_token);
      await AsyncStorage.setItem('refreshToken', data.refresh_token);
      await AsyncStorage.setItem('username', data.username);

      // ✅ Trigger AuthContext login
      await login({
        username: data.username,
        accessToken: data.access_token,
      });

      // ⚠️ No need to do navigation.replace("Main")
      // RootNavigator in App.js will auto-switch to AppStack
    } catch (error) {
      console.error('Login error:', error);
      if (Platform.OS !== 'web') {
        Alert.alert(
          'Login Failed',
          'Invalid credentials or network error. Please try again.'
        );
      } else {
        window.alert(
          'Login Failed, Invalid credentials or network error. Please try again.'
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-white px-6 justify-center">
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        className="flex-1 justify-center"
      >
        <View className="w-full max-w-80 mx-auto">
          <Text className="text-3xl font-bold text-indigo-700 text-center mb-10">
            Login to DSAExplorer
          </Text>

          <TextInput
            className="border border-gray-300 rounded-xl px-4 py-3 mb-6 text-base text-gray-900"
            placeholder="Email or Username"
            keyboardType="email-address"
            autoCapitalize="none"
            value={email}
            onChangeText={setEmail}
            placeholderTextColor="#9CA3AF"
            editable={!isLoading}
          />

          <View className="relative mb-8">
            <TextInput
              className="border border-gray-300 rounded-xl px-4 py-3 text-base text-gray-900 pr-12"
              placeholder="Password"
              secureTextEntry={!showPassword}
              value={password}
              onChangeText={setPassword}
              placeholderTextColor="#9CA3AF"
              editable={!isLoading}
              onSubmitEditing={handleLogin}
            />
            <TouchableOpacity
              className="absolute right-4 top-3"
              onPress={() => setShowPassword(!showPassword)}
              activeOpacity={0.7}
              accessibilityLabel={showPassword ? 'Hide password' : 'Show password'}
              disabled={isLoading}
            >
              <Feather
                name={showPassword ? 'eye-off' : 'eye'}
                size={24}
                color="#6B7280"
              />
            </TouchableOpacity>
          </View>

          <TouchableOpacity
            className="bg-indigo-600 rounded-xl py-4 mb-4"
            onPress={handleLogin}
            activeOpacity={0.8}
            accessibilityRole="button"
            accessibilityLabel="Login"
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text className="text-white text-center text-lg font-semibold">
                Login
              </Text>
            )}
          </TouchableOpacity>

          <View className="flex-row justify-center">
            <Text className="text-gray-600 mr-2">Don't have an account?</Text>
            <TouchableOpacity
              onPress={() => navigation.navigate('Register')}
              disabled={isLoading}
            >
              <Text className="text-indigo-600 font-semibold">Register</Text>
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};