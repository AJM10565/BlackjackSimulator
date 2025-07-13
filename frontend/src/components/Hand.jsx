import React from 'react';
import Card from './Card';

const Hand = ({ hand, isDealer = false, hideFirstCard = false, isActive = false }) => {
  return (
    <div className={`p-4 rounded-lg ${isActive ? 'ring-4 ring-yellow-400' : ''}`}>
      <div className="flex gap-2 justify-center">
        {hand.cards.map((card, index) => (
          <Card 
            key={index} 
            card={card} 
            hidden={isDealer && index === 0 && hideFirstCard}
          />
        ))}
      </div>
      <div className="text-center mt-2">
        <p className="text-lg font-semibold text-white">
          {isDealer ? 'Dealer' : 'Player'} 
          {!hideFirstCard && (
            <span className="ml-2">
              Value: {hand.value}
              {hand.is_soft && !hand.is_bust && ' (soft)'}
              {hand.is_blackjack && ' - Blackjack!'}
              {hand.is_bust && ' - Bust!'}
            </span>
          )}
        </p>
        {!isDealer && hand.bet > 0 && (
          <p className="text-sm text-yellow-300">Bet: ${hand.bet}</p>
        )}
      </div>
    </div>
  );
};

export default Hand;