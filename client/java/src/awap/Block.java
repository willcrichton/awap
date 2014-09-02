package awap;

import java.util.List;
import java.util.Map;

import com.google.common.base.Function;
import com.google.common.collect.Lists;

public class Block {
	private List<Point> offsets;

	public Block() {
	}

	public Block(List<Map<String, Integer>> offsets) {
		this.offsets = Lists.transform(offsets,
				new Function<Map<String, Integer>, Point>() {
					public Point apply(Map<String, Integer> map) {
						return new Point(map);
					}
				});
	}

	public List<Point> getOffsets() {
		return offsets;
	}

	public void setOffsets(List<Point> offsets) {
		this.offsets = offsets;
	}

	public Block rotate(final int rotations) {
		if (rotations == 0) {
			return this;
		}

		Block block = new Block();
		block.setOffsets(Lists.transform(offsets, new Function<Point, Point>() {
			public Point apply(Point p) {
				return p.rotate(rotations);
			}
		}));

		return block;
	}
}
