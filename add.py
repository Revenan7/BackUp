from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import TIMESTAMP
from datetime import datetime, timedelta
import pandas as pd


DATABASE_URL = "postgresql+psycopg2://postgres:123456@host.docker.internal:5440/original"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Определение моделей
class Device(Base):
    __tablename__ = 'device'
    ip_adress = Column(String, primary_key=True)  
    port = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    registers = relationship("Register", back_populates="device", cascade="all, delete-orphan")


class Register(Base):
    __tablename__ = 'registers'
    ip_device = Column(String, ForeignKey('device.ip_adress', ondelete="CASCADE"), primary_key=True)
    register_adress = Column(Integer, primary_key=True)  
    timestamp = Column(TIMESTAMP, default=datetime.utcnow, primary_key=True)
    type = Column(Text, nullable=False)
    value = Column(Text, nullable=False)
    device = relationship("Device", back_populates="registers")



Base.metadata.create_all(engine)

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()



def add_test_data():
    devices = [
        Device(ip_adress='192.168.1.1', port=502, name="Modbus Device 1"),
        Device(ip_adress='192.168.1.2', port=503, name="Modbus Device 2"),
        Device(ip_adress='192.168.1.3', port=504, name="Modbus Device 3")
    ]
    

    session.add_all(devices)
    session.commit()


    for device in devices:
        base_time = datetime(2025, 1, 1, 12, 0, 0)
        for i in range(10): 
            timestamp = base_time + timedelta(weeks=i * 6)  
            register = Register(
                ip_device=device.ip_adress,
                register_adress=i + 1,  
                type="int" if i % 2 == 0 else "float",  
                value=str(i * 10),  
                timestamp=timestamp
            )
            session.add(register)

    session.commit()
    print("Тестовые данные добавлены.")


if __name__ == '__main__':
    add_test_data()