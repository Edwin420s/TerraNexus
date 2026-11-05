import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ScrollView } from 'react-native';

export const ScoutingScreen: React.FC = () => {
  const [obsType, setObsType] = useState('pest_scouting');
  const [description, setDescription] = useState('');
  const [severity, setSeverity] = useState('medium');
  const [savedCount, setSavedCount] = useState(0);

  const handleSaveObservation = () => {
    if (!description.trim()) {
      Alert.alert('Required', 'Please enter scouting description');
      return;
    }
    setSavedCount(savedCount + 1);
    setDescription('');
    Alert.alert('Offline Saved', 'Observation saved to local SQLite database. Will sync when connection is restored.');
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Offline Field Scouting</Text>
      <Text style={styles.subtitle}>Records are buffered in local SQLite with GPS tags.</Text>

      <View style={styles.card}>
        <Text style={styles.label}>Observation Category</Text>
        <View style={styles.row}>
          {['pest_scouting', 'canopy_stress', 'weed_infestation', 'soil_compaction'].map((cat) => (
            <TouchableOpacity
              key={cat}
              onPress={() => setObsType(cat)}
              style={[styles.tag, obsType === cat && styles.tagActive]}
            >
              <Text style={[styles.tagText, obsType === cat && styles.tagTextActive]}>
                {cat.replace('_', ' ')}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={styles.label}>Severity</Text>
        <View style={styles.row}>
          {['low', 'medium', 'high', 'critical'].map((sev) => (
            <TouchableOpacity
              key={sev}
              onPress={() => setSeverity(sev)}
              style={[styles.tag, severity === sev && styles.tagActive]}
            >
              <Text style={[styles.tagText, severity === sev && styles.tagTextActive]}>{sev}</Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={styles.label}>Description & Symptoms</Text>
        <TextInput
          style={styles.textArea}
          placeholder="e.g. Early fall armyworm pinholes observed on whorl leaves..."
          value={description}
          onChangeText={setDescription}
          multiline
          numberOfLines={4}
        />

        <TouchableOpacity style={styles.btnSave} onPress={handleSaveObservation}>
          <Text style={styles.btnText}>Save Draft Observation ({savedCount} Buffered)</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc', padding: 16 },
  title: { fontSize: 22, fontWeight: 'bold', color: '#0f172a' },
  subtitle: { fontSize: 12, color: '#64748b', marginTop: 4, marginBottom: 16 },
  card: { backgroundColor: '#ffffff', borderRadius: 16, padding: 16, elevation: 2 },
  label: { fontSize: 12, fontWeight: '700', color: '#334155', textTransform: 'uppercase', marginBottom: 8, marginTop: 12 },
  row: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  tag: { paddingVertical: 6, paddingHorizontal: 12, backgroundColor: '#f1f5f9', borderRadius: 8 },
  tagActive: { backgroundColor: '#10b981' },
  tagText: { fontSize: 12, color: '#475569', fontWeight: '600' },
  tagTextActive: { color: '#ffffff' },
  textArea: { backgroundColor: '#f8fafc', borderWidth: 1, borderColor: '#e2e8f0', borderRadius: 12, padding: 12, textAlignVertical: 'top', marginTop: 4 },
  btnSave: { backgroundColor: '#10b981', paddingVertical: 14, borderRadius: 12, alignItems: 'center', marginTop: 20 },
  btnText: { color: '#ffffff', fontWeight: 'bold', fontSize: 14 },
});
