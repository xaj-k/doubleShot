if __name__ == "__main__":
    try:
        root.mainloop()
        while True:
            event = q.get()
            if event == GameEvent.TIMER_EXPIRED:
                pass
            elif event == GameEvent.HOME_SCORED:
                if gameState == GameState.ANSWERING:
                    if homeIsCorrect:
                        # pause time
                        # increment score
                        # update score display
                        # clear question/answer displays
                        # sound correct buzzer
                        # generate new question after 1 second and resume time
                        gameState = GameState.CORRECT
                    else:
                        # pause time
                        # show answer
                        # sound wrong buzzer
                        # generate new question after 1 second and resume time
                        gameState = GameState.INCORRECT
                elif gameState == GameState.IDLE:
                    # todo call start_new_game()
                        # note that new game will set gameState = GameState.ANSWERING
                        # generate a question based on button settings
                        # start the timer
                        # reset score to zero
                        # update all displays
                    pass
            elif event == GameEvent.VISITOR_SCORED:
                # do same as HOME_SCORED except check if not homeIsCorrect
                pass
            elif event == GameEvent.BUTTON_PRESSED:
                pass
            # do stuf
            q.task_done()
    except KeyboardInterrupt:
        pass
        # todo clean up
       