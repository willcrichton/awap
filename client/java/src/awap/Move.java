package awap;

public class Move {
	int index;
	int rotations;
	int x;
	int y;

	public Move(int index, int rotations, int x, int y) {
		this.index = index;
		this.rotations = rotations;
		this.x = x;
		this.y = y;
	}

	public int getIndex() {
		return index;
	}

	public void setIndex(int index) {
		this.index = index;
	}

	public int getRotations() {
		return rotations;
	}

	public void setRotations(int rotations) {
		this.rotations = rotations;
	}

	public int getX() {
		return x;
	}

	public void setX(int x) {
		this.x = x;
	}

	public int getY() {
		return y;
	}

	public void setY(int y) {
		this.y = y;
	}

	@Override
	public String toString() {
		return String.format("%d %d %d %d", index, rotations, x, y);
	}
}
