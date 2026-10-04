import React, { createContext, useContext, useEffect, useState } from "react";
import {
  type User,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut as firebaseSignOut,
  sendEmailVerification,
  sendPasswordResetEmail,
  updateProfile,
  onAuthStateChanged,
} from "firebase/auth";
import { auth, isFirebaseConfigured } from "../services/firebase";
import { setAuthToken } from "../services/api";

interface AuthContextType {
  currentUser: User | null;
  loading: boolean;
  isEmailVerified: boolean;
  isConfigured: boolean;
  signup: (email: string, password: string, displayName: string) => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  resendVerification: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  refreshUser: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const isConfigured = isFirebaseConfigured();

  useEffect(() => {
    if (!isConfigured) {
      setLoading(false);
      return;
    }

    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setCurrentUser(user);
      if (user) {
        try {
          const token = await user.getIdToken();
          setAuthToken(token);
        } catch {
          setAuthToken(null);
        }
      } else {
        setAuthToken(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, [isConfigured]);

  const signup = async (email: string, password: string, displayName: string) => {
    if (!isConfigured) {
      throw new Error(
        "Firebase is not yet configured. Please set your Firebase Web App credentials in frontend/.env."
      );
    }
    const cred = await createUserWithEmailAndPassword(auth, email, password);
    if (displayName) {
      await updateProfile(cred.user, { displayName });
    }
    await sendEmailVerification(cred.user);
  };

  const login = async (email: string, password: string) => {
    if (!isConfigured) {
      throw new Error(
        "Firebase is not yet configured. Please set your Firebase Web App credentials in frontend/.env."
      );
    }
    const cred = await signInWithEmailAndPassword(auth, email, password);
    const token = await cred.user.getIdToken();
    setAuthToken(token);
  };

  const logout = async () => {
    if (!isConfigured) return;
    await firebaseSignOut(auth);
    setAuthToken(null);
  };

  const resendVerification = async () => {
    if (!currentUser) {
      throw new Error("No signed-in user found to send verification to.");
    }
    await sendEmailVerification(currentUser);
  };

  const resetPassword = async (email: string) => {
    if (!isConfigured) {
      throw new Error("Firebase is not yet configured.");
    }
    await sendPasswordResetEmail(auth, email);
  };

  const refreshUser = async (): Promise<boolean> => {
    if (!currentUser) return false;
    await currentUser.reload();
    setCurrentUser(auth.currentUser);
    return Boolean(auth.currentUser?.emailVerified);
  };

  const isEmailVerified = Boolean(currentUser?.emailVerified);

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        loading,
        isEmailVerified,
        isConfigured,
        signup,
        login,
        logout,
        resendVerification,
        resetPassword,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
