package awap;

import java.util.List;
import java.util.Map;

import com.google.common.base.Optional;
import com.google.common.collect.Lists;

public class State {
	private Optional<String> error = Optional.absent();
	private Optional<Integer> number = Optional.absent();
	private List<List<Integer>> board;
	private List<List<Block>> blocks;
	private int dimension;
	private int turn;
	private int move = -1;
	private String url;
	private List<List<Integer>> bonusSquares;

	public String getUrl() {
		return url;
	}

	public void setUrl(String url) {
		this.url = url;
	}

	public Optional<String> getError() {
		return error;
	}

	public void setError(String error) {
		this.error = Optional.fromNullable(error);
	}

	public Optional<Integer> getNumber() {
		return number;
	}

	public void setNumber(int number) {
		this.number = Optional.fromNullable(number);
	}

	public List<List<Integer>> getBoard() {
		return board;
	}

	@SuppressWarnings("unchecked")
	public void setBoard(Map<String, Object> board) {
		this.board = (List<List<Integer>>) board.get("grid");
    this.bonusSquares = (List<List<Integer>>) board.get("bonus_squares");
		this.setDimension((int) board.get("dimension"));
	}

	public int getMove() {
		return move;
	}

	public void setMove(int move) {
		this.move = move;
	}

	public int getDimension() {
		return dimension;
	}

	public void setDimension(int dimension) {
		this.dimension = dimension;
	}

	public int getTurn() {
		return turn;
	}

	public void setTurn(int turn) {
		this.turn = turn;
	}

	public List<List<Block>> getBlocks() {
		return blocks;
	}

	public void setBlocks(List<List<List<Map<String, Integer>>>> blocks) {
		List<List<Block>> blockList = Lists.newArrayList();
		for (List<List<Map<String, Integer>>> player : blocks) {
			List<Block> playerList = Lists.newArrayList();
			for (List<Map<String, Integer>> block : player) {
				playerList.add(new Block(block));
			}
			blockList.add(playerList);
		}

		this.blocks = blockList;
	}

	public List<List<Integer>> getBonusSquares() {
		return bonusSquares;
	}

  public void setPlayers(List<String> players) {}
}
