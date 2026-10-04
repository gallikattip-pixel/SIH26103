import { initializeApp, getApps, getApp, type FirebaseApp } from "firebase/app";
import { getAuth, type Auth } from "firebase/auth";
import { getDatabase, type Database } from "firebase/database";
import { getStorage, type FirebaseStorage } from "firebase/storage";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "",
  databaseURL: import.meta.env.VITE_FIREBASE_DATABASE_URL || "",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "",
};

export const isFirebaseConfigured = (): boolean => {
  return Boolean(
    firebaseConfig.apiKey &&
    firebaseConfig.authDomain &&
    firebaseConfig.projectId
  );
};

let app: FirebaseApp;
let auth: Auth;
let db: Database | null = null;
let storage: FirebaseStorage | null = null;

if (isFirebaseConfigured()) {
  app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApp();
  auth = getAuth(app);
  if (firebaseConfig.databaseURL) {
    db = getDatabase(app);
  }
  if (firebaseConfig.storageBucket) {
    storage = getStorage(app);
  }
} else {
  // If not configured, initialize placeholder app so imports don't crash before credentials are added
  app = getApps().length === 0 ? initializeApp({
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: "infraplus-placeholder.firebaseapp.com",
    projectId: "infraplus-placeholder",
  }) : getApp();
  auth = getAuth(app);
}

export { app, auth, db, storage };
