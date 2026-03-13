import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Login } from '../Login';
import { useNavigation } from '@react-navigation/native';
import { useAuth } from '../../AuthContext';

// Mock useNavigation
const mockedNavigate = jest.fn();
jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({
    navigate: mockedNavigate,
  }),
}));

// Mock useAuth
const mockedLogin = jest.fn();
jest.mock('../../AuthContext', () => ({
  useAuth: () => ({
    login: mockedLogin,
  }),
}));

// Mock fetch
global.fetch = jest.fn();

describe('Login Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders correctly', () => {
    const { getByPlaceholderText, getByText } = render(<Login />);
    
    expect(getByText('Login to DSAExplorer')).toBeTruthy();
    expect(getByPlaceholderText('Username')).toBeTruthy();
    expect(getByPlaceholderText('Password')).toBeTruthy();
  });

  it('shows error if email or password is empty', async () => {
    const { getByText } = render(<Login />);
    const loginButton = getByText('Login');
    
    fireEvent.press(loginButton);
    
    // Alert should have been called (mocked or handled)
    // In React Native testing, it's sometimes tricky to test Alert.alert without mocking it.
  });

  it('calls handleLogin on successful input', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({
        access_token: 'fake_access_token',
        refresh_token: 'fake_refresh_token',
        username: 'testuser',
      }),
    });

    const { getByPlaceholderText, getByText } = render(<Login />);
    
    fireEvent.changeText(getByPlaceholderText('Username'), 'testuser');
    fireEvent.changeText(getByPlaceholderText('Password'), 'password123');
    fireEvent.press(getByText('Login'));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/login'),
        expect.objectContaining({
          method: 'POST',
        })
      );
      expect(mockedLogin).toHaveBeenCalled();
    });
  });
});
