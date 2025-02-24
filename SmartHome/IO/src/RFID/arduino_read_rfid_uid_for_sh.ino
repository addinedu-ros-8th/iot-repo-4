// 필요한 라이브러리 포함
#include <SPI.h>        // SPI 통신을 위한 표준 라이브러리 (RFID 모듈과 통신)
#include <MFRC522.h>    // MFRC522 (RFID 리더기) 라이브러리 (카드 UID 읽기 기능 제공)
#include <List.hpp>     // 동적 리스트를 사용하기 위한 라이브러리 (UID 저장용, 표준 라이브러리 아님)

// RFID 모듈 핀 정의
#define RST_PIN 9   // MFRC522 리셋 핀 (Reset 핀 연결)
#define SS_PIN 10   // SPI 통신에서 Slave Select (SS) 핀 (칩 선택)

// RFID 태그 리스트 (등록된 UID 저장 공간) → 동적 리스트 사용
List<MFRC522::Uid> tag_list; // UID 목록을 저장하는 리스트 객체 생성

// MFRC522 객체 생성 (RFID 모듈 제어용)
MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(9600);  // 시리얼 통신 시작 (9600bps 속도로 설정)
  while (!Serial);     // 시리얼 포트가 열릴 때까지 대기 (특히 ATMEGA32U4 기반 보드에서 필요)

  SPI.begin();         // SPI 통신 초기화 (RFID 모듈과 통신하기 위해 필요)
  mfrc522.PCD_Init();  // MFRC522 모듈 초기화
  delay(4);            // 초기화 후 안정적인 동작을 위해 약간의 지연 (일부 보드에서는 필수)

  // MFRC522 모듈의 펌웨어 버전을 출력하여 모듈이 정상적으로 연결되었는지 확인
  mfrc522.PCD_DumpVersionToSerial();
  
  Serial.println("RFID 태그를 스캔하세요.");  // 사용자에게 태그 스캔을 요청하는 메시지 출력
}

void loop() {
  // 1. 새로운 RFID 태그(카드)가 인식되었는지 확인
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return;  // 카드가 감지되지 않으면 루프 종료 (다음 루프에서 다시 확인)
  }

  // 2. 카드의 데이터를 읽을 수 있는지 확인
  if (!mfrc522.PICC_ReadCardSerial()) {
    return;  // 카드 데이터를 읽을 수 없으면 루프 종료 (다음 루프에서 다시 확인)
  }

  // 3. 읽은 RFID UID 값을 시리얼 모니터에 출력
  Serial.print("UID: ");
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");  // 앞자리가 한 자리일 경우 0 추가
    Serial.print(mfrc522.uid.uidByte[i], HEX); // 16진수(HEX) 형식으로 UID 출력
  }
  Serial.println();  // UID 출력 후 줄 바꿈

  // 4. 현재 읽은 UID가 이미 저장된 태그 리스트에 있는지 확인
  bool registered = false;  // 초기 상태: 등록되지 않은 태그로 설정

  for (int i = 0; i < tag_list.getSize(); i++) {
    // 기존 리스트의 UID와 새로 읽은 UID를 비교 (memcmp 사용)
    if (memcmp(tag_list.get(i).uidByte, mfrc522.uid.uidByte, 4) == 0) {
      registered = true;  // 동일한 UID가 존재하면 등록된 태그로 설정
      break;  // UID를 찾았으므로 더 이상 검사할 필요 없음
    }
  }

  // 5. 등록되지 않은 새로운 RFID 태그라면 리스트에 추가
  if (!registered) {
    tag_list.addLast(mfrc522.uid); // 동적 리스트에 UID 추가
    Serial.println("새로운 RFID 태그가 등록되었습니다.");
  } else {
    Serial.println("이미 등록된 RFID 태그입니다.");
  }

  // 6. 등록된 RFID 태그 리스트 출력 (UID 목록을 시리얼 모니터에 표시)
  Serial.print("등록된 태그 리스트 (");
  Serial.print(tag_list.getSize());  // 현재 등록된 UID 개수 출력
  Serial.print("개):");
  Serial.println();

  for (int i = 0; i < tag_list.getSize(); i++) {
    for (byte j = 0; j < 4; j++) { // UID는 4바이트 길이
      Serial.print(tag_list.get(i).uidByte[j] < 0x10 ? " 0" : " ");
      Serial.print(tag_list.get(i).uidByte[j], HEX); // 16진수로 출력
    }
    Serial.println();  // 각 UID를 출력 후 줄 바꿈
  }

  Serial.println();  // 전체 리스트 출력 후 줄 바꿈
  delay(1000);  // 1초 대기 후 다시 태그를 읽음 (연속 읽기 방지)
}
