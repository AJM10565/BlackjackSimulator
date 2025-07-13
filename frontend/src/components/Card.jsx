import React from 'react';

const Card = ({ card, hidden = false }) => {
  if (hidden) {
    return (
      <div className="w-20 h-28 bg-blue-800 rounded-lg shadow-lg flex items-center justify-center border-2 border-white">
        <div className="text-white text-4xl">?</div>
      </div>
    );
  }

  const isRed = card.suit === '♥' || card.suit === '♦';
  const textColor = isRed ? 'text-red-600' : 'text-black';

  return (
    <div className="w-20 h-28 bg-white rounded-lg shadow-lg border-2 border-gray-300 flex flex-col justify-between p-2">
      <div className={`text-xl font-bold ${textColor}`}>
        {card.rank}
        <span className="text-2xl">{card.suit}</span>
      </div>
      <div className={`text-4xl self-center ${textColor}`}>
        {card.suit}
      </div>
      <div className={`text-xl font-bold self-end rotate-180 ${textColor}`}>
        {card.rank}
        <span className="text-2xl">{card.suit}</span>
      </div>
    </div>
  );
};

export default Card;