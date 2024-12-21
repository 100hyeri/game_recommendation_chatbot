import React from 'react';
import './modalStyles.css';

const GameDetailModal = ({ game, onClose }) => {
  if (!game) return null;

  return (
    <div className="modal">
      <div className="modal-content">
        <h2>{game.name}</h2>
        <p>{game.description || '설명이 없습니다.'}</p>
        {game.image && <img src={game.image} alt={game.name} />}
        <button onClick={onClose}>닫기</button>
      </div>
    </div>
  );
};

export default GameDetailModal;
