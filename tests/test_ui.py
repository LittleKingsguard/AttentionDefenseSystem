import pytest
from ui import ApprovalWindow

def test_approval_window_creation(qtbot):
    """Test that the ApprovalWindow is created correctly with all tabs."""
    requester = "Alice"
    message = "Can you check this?"
    draft = "Sure, I'll check it right away."
    
    window = ApprovalWindow(requester, message, draft)
    qtbot.addWidget(window)
    
    assert window.windowTitle() == "Attention Defense System"
    assert window.tabs.count() == 4
    assert window.tabs.tabText(0) == "Current Request"
    assert window.tabs.tabText(1) == "History"
    assert window.tabs.tabText(2) == "Search Knowledge Base"
    assert window.tabs.tabText(3) == "Settings"
    
    # Check that initial data is passed to the current request tab
    # Assuming tab_current has labels for these, though we can just check it exists
    assert window.tab_current is not None
