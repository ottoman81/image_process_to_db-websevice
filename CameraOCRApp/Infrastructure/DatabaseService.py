import pyodbc
from typing import List, Optional
from datetime import datetime
from Domain.Models import DatabaseConfig, SensorData

class DatabaseService:
    def __init__(self):
        self.connection = None
        self.config = DatabaseConfig()
        
    def test_connection(self, config: DatabaseConfig) -> tuple[bool, str]:
        """Veritabanı bağlantısını test et"""
        try:
            conn = self._create_connection(config)
            if conn:
                conn.close()
                return True, "Bağlantı başarılı!"
            return False, "Bağlantı oluşturulamadı"
        except Exception as e:
            return False, f"Bağlantı hatası: {str(e)}"
    
    def _create_connection(self, config: DatabaseConfig):
        """Veritabanı bağlantısı oluştur"""
        try:
            if config.connection_string:
                conn_str = config.connection_string
            else:
                if config.use_windows_auth:
                    conn_str = f"""
                        DRIVER={{ODBC Driver 17 for SQL Server}};
                        SERVER={config.server},{config.port};
                        DATABASE={config.database};
                        Trusted_Connection=yes;
                    """
                else:
                    conn_str = f"""
                        DRIVER={{ODBC Driver 17 for SQL Server}};
                        SERVER={config.server},{config.port};
                        DATABASE={config.database};
                        UID={config.username};
                        PWD={config.password};
                    """
            
            return pyodbc.connect(conn_str)
        except Exception as e:
            raise Exception(f"Bağlantı hatası: {str(e)}")
    
    def connect(self, config: DatabaseConfig) -> tuple[bool, str]:
        """Veritabanına bağlan"""
        try:
            self.config = config
            self.connection = self._create_connection(config)
            return True, "Bağlantı başarılı!"
        except Exception as e:
            return False, f"Bağlantı hatası: {str(e)}"
    
    def disconnect(self):
        """Bağlantıyı kes"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def is_connected(self) -> bool:
        """Bağlantı durumunu kontrol et"""
        return self.connection is not None
    
    def create_table(self):
        """SensorData tablosunu oluştur"""
        if not self.connection:
            return False, "Önce bağlantı kurulmalı"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='SensorData' AND xtype='U')
                CREATE TABLE SensorData (
                    Id INT IDENTITY(1,1) PRIMARY KEY,
                    Temperature FLOAT NOT NULL,
                    Humidity FLOAT NOT NULL,
                    Timestamp DATETIME2 NOT NULL
                )
            """)
            self.connection.commit()
            return True, "Tablo oluşturuldu/var"
        except Exception as e:
            return False, f"Tablo oluşturma hatası: {str(e)}"
    
    def insert_sensor_data(self, data: SensorData) -> tuple[bool, str]:
        """Sensör verisi ekle"""
        if not self.connection:
            return False, "Önce bağlantı kurulmalı"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO SensorData (Temperature, Humidity, Timestamp)
                VALUES (?, ?, ?)
            """, data.temperature, data.humidity, data.timestamp)
            
            self.connection.commit()
            return True, "Veri başarıyla eklendi"
        except Exception as e:
            return False, f"Veri ekleme hatası: {str(e)}"
    
    def get_all_data(self) -> List[SensorData]:
        """Tüm sensör verilerini getir"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT Id, Temperature, Humidity, Timestamp FROM SensorData ORDER BY Timestamp DESC")
            
            results = []
            for row in cursor.fetchall():
                results.append(SensorData(
                    id=row.Id,
                    temperature=row.Temperature,
                    humidity=row.Humidity,
                    timestamp=row.Timestamp
                ))
            
            return results
        except Exception as e:
            print(f"Veri getirme hatası: {str(e)}")
            return []
    
    def get_last_n_records(self, n: int = 10) -> List[SensorData]:
        """Son n kaydı getir"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT TOP (?) Id, Temperature, Humidity, Timestamp 
                FROM SensorData 
                ORDER BY Timestamp DESC
            """, n)
            
            results = []
            for row in cursor.fetchall():
                results.append(SensorData(
                    id=row.Id,
                    temperature=row.Temperature,
                    humidity=row.Humidity,
                    timestamp=row.Timestamp
                ))
            
            return results
        except Exception as e:
            print(f"Veri getirme hatası: {str(e)}")
            return []