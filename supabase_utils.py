from supabase_client import supabase
from typing import Dict, List, Any, Optional

# Adopsi related functions
def get_all_adopsi() -> List[Dict[str, Any]]:
    return supabase.table('adopsi').select('*').execute().data

def get_adopsi_by_id(id_adopsi: str) -> Optional[Dict[str, Any]]:
    result = supabase.table('adopsi').select('*').eq('id_adopsi', id_adopsi).execute().data
    return result[0] if result else None

# Adopter related functions
def get_all_adopter() -> List[Dict[str, Any]]:
    return supabase.table('adopter').select('*').execute().data

def get_adopter_by_id(id_adopter: str) -> Optional[Dict[str, Any]]:
    result = supabase.table('adopter').select('*').eq('id_adopter', id_adopter).execute().data
    return result[0] if result else None

def get_adopter_by_username(username: str) -> Optional[Dict[str, Any]]:
    result = supabase.table('adopter').select('*').eq('username_adopter', username).execute().data
    return result[0] if result else None

# Atraksi related functions
def get_all_atraksi() -> List[Dict[str, Any]]:
    return supabase.table('atraksi').select('*').execute().data

def get_atraksi_by_id(id_atraksi: str) -> Optional[Dict[str, Any]]:
    result = supabase.table('atraksi').select('*').eq('id_atraksi', id_atraksi).execute().data
    return result[0] if result else None

# Berpartisipasi related functions
def get_all_berpartisipasi() -> List[Dict[str, Any]]:
    return supabase.table('berpartisipasi').select('*').execute().data

# Catatan Medis related functions
def get_all_catatan_medis() -> List[Dict[str, Any]]:
    return supabase.table('catatan_medis').select('*').execute().data

def get_catatan_medis_by_id(id_hewan: str) -> List[Dict[str, Any]]:
    return supabase.table('catatan_medis').select('*').eq('id_hewan', id_hewan).execute().data

# Dokter Hewan related functions
def get_all_dokter_hewan() -> List[Dict[str, Any]]:
    return supabase.table('dokter_hewan').select('*').execute().data

def get_dokter_by_id(username_dh: str) -> Optional[Dict[str, Any]]:
    result = supabase.table('dokter_hewan').select('*').eq('username_dh', username_dh).execute().data
    return result[0] if result else None

# Fasilitas related functions
def get_all_fasilitas() -> List[Dict[str, Any]]:
    return supabase.table('fasilitas').select('*').execute().data

# Habitat related functions
def get_all_habitat() -> List[Dict[str, Any]]:
    return supabase.table('habitat').select('*').execute().data

def get_habitat_by_id(nama_habitat: str) -> Optional[Dict[str, Any]]:
    result = supabase.table('habitat').select('*').eq('nama_habitat', nama_habitat).execute().data
    return result[0] if result else None

# Hewan related functions
def get_all_hewan() -> List[Dict[str, Any]]:
    return supabase.table('hewan').select('*').execute().data

def get_hewan_by_id(id_hewan: str) -> Optional[Dict[str, Any]]:
    result = supabase.table('hewan').select('*').eq('id', id_hewan).execute().data
    return result[0] if result else None

# Individu related functions
def get_all_individu() -> List[Dict[str, Any]]:
    return supabase.table('individu').select('*').execute().data

def get_individu_by_id(id_adopter: str) -> Optional[Dict[str, Any]]:
    result = supabase.table('individu').select('*').eq('id_adopter', id_adopter).execute().data
    return result[0] if result else None

# Jadwal Pemeriksaan Kesehatan related functions
def get_all_jadwal_pemeriksaan() -> List[Dict[str, Any]]:
    return supabase.table('jadwal_pemeriksaan_kesehatan').select('*').execute().data

# Jadwal Penugasan related functions
def get_all_jadwal_penugasan() -> List[Dict[str, Any]]:
    return supabase.table('jadwal_penugasan').select('*').execute().data

def get_jadwal_by_username(username_ph: str) -> List[Dict[str, Any]]:
    return supabase.table('jadwal_penugasan').select('*').eq('username_ph', username_ph).execute().data

# Memberi related functions
def get_all_memberi() -> List[Dict[str, Any]]:
    return supabase.table('memberi').select('*').execute().data

# Organisasi related functions
def get_all_organisasi() -> List[Dict[str, Any]]:
    return supabase.table('organisasi').select('*').execute().data

def get_organisasi_by_id(id_adopter: str) -> Optional[Dict[str, Any]]:
    result = supabase.table('organisasi').select('*').eq('id_adopter', id_adopter).execute().data
    return result[0] if result else None

# Pakan related functions
def get_all_pakan() -> List[Dict[str, Any]]:
    return supabase.table('pakan').select('*').execute().data

def get_pakan_by_id(id_hewan: str) -> List[Dict[str, Any]]:
    return supabase.table('pakan').select('*').eq('id_hewan', id_hewan).execute().data

# Pelatih Hewan related functions
def get_all_pelatih_hewan() -> List[Dict[str, Any]]:
    return supabase.table('pelatih_hewan').select('*').execute().data

def get_pelatih_by_username(username_ph: str) -> Optional[Dict[str, Any]]:
    result = supabase.table('pelatih_hewan').select('*').eq('username_ph', username_ph).execute().data
    return result[0] if result else None

# Pengguna related functions
def get_all_pengguna() -> List[Dict[str, Any]]:
    return supabase.table('pengguna').select('*').execute().data

def get_pengguna_by_username(username: str) -> Optional[Dict[str, Any]]:
    result = supabase.table('pengguna').select('*').eq('username', username).execute().data
    return result[0] if result else None

# Pengunjung related functions
def get_all_pengunjung() -> List[Dict[str, Any]]:
    return supabase.table('pengunjung').select('*').execute().data

def get_pengunjung_by_username(username_p: str) -> Optional[Dict[str, Any]]:
    result = supabase.table('pengunjung').select('*').eq('username_p', username_p).execute().data
    return result[0] if result else None

# Penjaga Hewan related functions
def get_all_penjaga_hewan() -> List[Dict[str, Any]]:
    return supabase.table('penjaga_hewan').select('*').execute().data

def get_penjaga_by_username(username_pj: str) -> Optional[Dict[str, Any]]:
    result = supabase.table('penjaga_hewan').select('*').eq('username_pj', username_pj).execute().data
    return result[0] if result else None

# Reservasi related functions
def get_all_reservasi() -> List[Dict[str, Any]]:
    return supabase.table('reservasi').select('*').execute().data

def get_reservasi_by_id(username_p: str) -> List[Dict[str, Any]]:
    return supabase.table('reservasi').select('*').eq('username_p', username_p).execute().data

# Spesialisasi related functions
def get_all_spesialisasi() -> List[Dict[str, Any]]:
    return supabase.table('spesialisasi').select('*').execute().data

# Staff Admin related functions
def get_all_staff_admin() -> List[Dict[str, Any]]:
    return supabase.table('staf_admin').select('*').execute().data

def get_admin_by_username(username_sa: str) -> Optional[Dict[str, Any]]:
    result = supabase.table('staf_admin').select('*').eq('username_sa', username_sa).execute().data
    return result[0] if result else None

# Wahana related functions
def get_all_wahana() -> List[Dict[str, Any]]:
    return supabase.table('wahana').select('*').execute().data

def get_wahana_by_nama(nama_wahana: str) -> Optional[Dict[str, Any]]:
    result = supabase.table('wahana').select('*').eq('nama_wahana', nama_wahana).execute().data
    return result[0] if result else None

# Create/Insert functions
def create_adopsi(data: Dict[str, Any]) -> Dict[str, Any]:
    return supabase.table('adopsi').insert(data).execute().data[0]

def create_adopter(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new adopter record"""
    return supabase.table('adopter').insert(data).execute().data[0]

def create_individu(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new individual adopter record"""
    return supabase.table('individu').insert(data).execute().data[0]

def create_organisasi(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new organization adopter record"""
    return supabase.table('organisasi').insert(data).execute().data[0]

def create_complete_adopter(adopter_data: Dict[str, Any], type_data: Dict[str, Any], is_individual: bool = True) -> Dict[str, Any]:
    """
    Create a complete adopter record with associated individual/organization data
    
    Args:
        adopter_data: Dictionary containing adopter table data
        type_data: Dictionary containing individu/organisasi table data
        is_individual: Boolean indicating if adopter is individual (True) or organization (False)
    
    Returns:
        Dictionary containing the created adopter data
    """
    # First create the adopter record
    adopter = create_adopter(adopter_data)
    
    # Add the id_adopter to the type data
    type_data['id_adopter'] = adopter['id_adopter']
    
    # Create the associated record based on type
    if is_individual:
        individu = create_individu(type_data)
        return {**adopter, 'detail': individu}
    else:
        organisasi = create_organisasi(type_data)
        return {**adopter, 'detail': organisasi}

def create_hewan(data: Dict[str, Any]) -> Dict[str, Any]:
    return supabase.table('hewan').insert(data).execute().data[0]

def create_catatan_medis(data: Dict[str, Any]) -> Dict[str, Any]:
    return supabase.table('catatan_medis').insert(data).execute().data[0]

def create_reservasi(data: Dict[str, Any]) -> Dict[str, Any]:
    return supabase.table('reservasi').insert(data).execute().data[0]

# Update functions
def update_adopsi(id_adopsi: str, data: Dict[str, Any]) -> Dict[str, Any]:
    return supabase.table('adopsi').update(data).eq('id_adopsi', id_adopsi).execute().data[0]

def update_hewan(id_hewan: str, data: Dict[str, Any]) -> Dict[str, Any]:
    return supabase.table('hewan').update(data).eq('id', id_hewan).execute().data[0]

def update_catatan_medis(id_hewan: str, tanggal: str, data: Dict[str, Any]) -> Dict[str, Any]:
    return supabase.table('catatan_medis').update(data).eq('id_hewan', id_hewan).eq('tanggal_pemeriksaan', tanggal).execute().data[0]

# Delete functions
def delete_adopsi(id_adopsi: str) -> Dict[str, Any]:
    return supabase.table('adopsi').delete().eq('id_adopsi', id_adopsi).execute().data[0]

def delete_adopter(id_adopter: str) -> None:
    """
    Delete an adopter and all related records.
    This will delete:
    1. All adoption records for this adopter
    2. The individu/organisasi record
    3. The adopter record itself
    """
    # First delete all adoptions
    supabase.table('adopsi').delete().eq('id_adopter', id_adopter).execute()
    
    # Delete from individu and organisasi (one of them will succeed)
    supabase.table('individu').delete().eq('id_adopter', id_adopter).execute()
    supabase.table('organisasi').delete().eq('id_adopter', id_adopter).execute()
    
    # Finally delete the adopter record
    supabase.table('adopter').delete().eq('id_adopter', id_adopter).execute()

def delete_reservasi(username_p: str, tanggal: str) -> Dict[str, Any]:
    return supabase.table('reservasi').delete().eq('username_p', username_p).eq('tanggal_kunjungan', tanggal).execute().data[0] 