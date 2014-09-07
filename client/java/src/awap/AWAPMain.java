package awap;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.base.Optional;

public class AWAPMain {
	public static void main(String[] args) throws IOException {
		BufferedReader reader = new BufferedReader(new InputStreamReader(
				System.in));
		String input;
		Game game = new Game();
		ObjectMapper objectMapper = new ObjectMapper();
		game.updateState(objectMapper.readValue(reader.readLine(), State.class));

		while ((input = reader.readLine()) != null) {
			State state = objectMapper.readValue(input, State.class);
			Optional<Move> move = game.updateState(state);

			if (move.isPresent()) {
				System.out.println(move.get());
			}
		}
	}
}
