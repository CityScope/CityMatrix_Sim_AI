import java.util.ArrayList;

public class Road {

	public ArrayList<Point> roadPoints;
	public Direction direction;
	
	public boolean horizontal() {
		return direction == Direction.Left || direction == Direction.Right;
	}
	
}