import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './styles.css';
import GameDetailModal from './GameDetailModal';

const GameRecommendation = () => {
  const [userInput, setUserInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedGame, setSelectedGame] = useState(null);

  // 컴포넌트가 마운트될 때 추천 게임 목록을 가져오는 함수
  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/recommendations');
      const fetchedRecommendations = response.data || [];
      
      // 데이터를 가져온 후, 게임 정보가 유효한지 확인하는 조건 추가
      const validRecommendations = fetchedRecommendations.filter(
        rec => rec && rec.game && rec.game.name // 유효한 게임 데이터만 추가
      );

      setRecommendations(validRecommendations);
    } catch (error) {
      console.error("추천 게임을 가져오는 동안 오류가 발생했습니다:", error);
      setRecommendations([]); // 오류 발생 시 빈 배열로 초기화
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const updatedChatHistory = [...chatHistory, { role: 'user', content: userInput }];
    setChatHistory(updatedChatHistory);

    try {
      const response = await axios.post('http://localhost:5000/api/chat', { input: userInput });
      const botResponse = response.data.response;
      const game = response.data.game; // 단일 게임으로 수정

      // 챗봇의 응답을 채팅 기록에 추가
      setChatHistory((prevHistory) => [
        ...prevHistory, 
        { role: 'bot', content: botResponse }
      ]);

      // 게임 정보가 유효한지 확인 후 추가
      if (game && game.name) {
        setRecommendations((prevRecommendations) => [...prevRecommendations, { game }]);
      }
    } catch (error) {
      console.error("챗봇 응답을 가져오는 동안 오류가 발생했습니다:", error);
    }

    setUserInput('');
  };

  const handleDelete = async (gameName) => {
    try {
      await axios.delete(`http://localhost:5000/api/recommendations/${encodeURIComponent(gameName)}`);
      setRecommendations((prevRecommendations) =>
        prevRecommendations.filter(rec => rec.game.name !== gameName)
      );
    } catch (error) {
      console.error("추천 게임을 삭제하는 동안 오류가 발생했습니다:", error);
    }
  };

  const handleGameClick = async (appId) => {
    try {
      const response = await axios.get(`http://localhost:5000/api/game/${appId}`);
      setSelectedGame(response.data); // 게임 세부 정보 저장
      setModalOpen(true); // 모달 열기
    } catch (error) {
      console.error("게임 정보를 가져오는 동안 오류가 발생했습니다:", error);
    }
  };

  const closeModal = () => {
    setModalOpen(false);
    setSelectedGame(null); // 선택된 게임 초기화
  };

  return (
    <div className="wrap">
      <header>
        <h1>스팀 게임 추천 챗봇</h1>
        <img src={process.env.PUBLIC_URL + '/chatbot.png'} alt="Chatbot" />
      </header>
      <div className="container">
        <div className="chat-history">
          {chatHistory.map((chat, index) => (
            <div key={index} className={chat.role}>
              <strong>{chat.role === 'user' ? 'User' : 'Bot'}:</strong> {chat.content}
            </div>
          ))}
        </div>
        <form onSubmit={handleSubmit} className="chat-form">
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="챗봇과 대화를 통해 기분을 표현해 보세요."
            className="input-field"
          />
          <button type="submit" className="submit-button">
            <img src={process.env.PUBLIC_URL + '/send.png'} alt="Send" />
          </button>
        </form>
        <h3>추천 게임 목록:</h3>
        <ul className="recommendation-list">
          {Array.isArray(recommendations) && recommendations.length > 0 ? (
            recommendations.map((rec, index) => (
              <li key={index} className="recommendation-item">
                {rec.game.name}
                <button 
                  onClick={() => handleGameClick(rec.game.appid)} 
                  className="detail-button"
                >
                  세부 정보 보기
                </button>
                <button 
                  onClick={() => handleDelete(rec.game.name)} 
                  className="delete-button"
                >
                  삭제
                </button>
              </li>
            ))
          ) : (
            <li>추천할 게임이 없습니다.</li>
          )}
        </ul>

        {modalOpen && (
          <GameDetailModal game={selectedGame} onClose={closeModal} />
        )}
      </div>
    </div>
  );
};

export default GameRecommendation;
