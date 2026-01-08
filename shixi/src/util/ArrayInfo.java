package util;

import java.util.ArrayList;

/**
 * ?????(?????)
 */
public class ArrayInfo {
	// ????
	private ArrayList<Integer> demenList = new ArrayList<>(); // JDK 7+ ????
	private int demenSize = 0; // ??

	public String getDemenString() {
		StringBuilder sb = new StringBuilder(); // ?? StringBuilder ????
		for (int i = 0; i < demenSize; i++) {
			sb.append("[]");
		}
		return sb.toString();
	}

	public void addDemenInfo(int newDemen) {
		if (newDemen <= 0 || newDemen > 32767) {
			System.out.println("????????: " + newDemen);
			newDemen = 1; // ????? 1
		}
		this.demenList.add(newDemen); // ??????? new Integer()
		setDemenSize();
	}

	public int getDemenSize() {
		return demenSize;
	}

	public void setDemenSize(int demenSize) {
		this.demenSize = demenSize;
	}

	public void setDemenSize() {
		this.demenSize = demenList.size();
	}


	public ArrayList<Integer> getDemenList() {
		return this.demenList;
	}

	@Override
	public String toString() {
		if (demenList == null || demenList.isEmpty()) {
			return "[]";
		}
		StringBuilder sb = new StringBuilder();
		sb.append("[");
		for (int i = 0; i < demenList.size(); i++) {
			sb.append(demenList.get(i));
			if (i < demenList.size() - 1) {
				sb.append(",");
			}
		}
		sb.append("]");
		return sb.toString();
	}

	public boolean checkArray(ArrayList<Integer> intList) {
		if (intList == null) return false;

		if (this.demenSize != intList.size()) {
			return false;
		}

		for (int i = 0; i < demenSize; i++) {
			int index = intList.get(i);
			int bound = this.demenList.get(i);
			// ?????????0 <= index < bound
			if (index < 0 || index >= bound) {
				return false;
			}
		}
		return true;
	}
}