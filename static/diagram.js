var RED_PLAYER = 0;
var WHITE_PLAYER = 1;

var CHECK_SIDE_LENGTH = 24;
var DIE_SIDE_LENGTH = 28;
var DICE_MARGIN = 10;
var OVERFLOW_INDICATOR_SIZE = 18;

function setDimensions() {
	HALF_CHECK_SIDE_LENGTH = CHECK_SIDE_LENGTH / 2;

	POINT_CAPACITY = 5;

	BAR_LEFT_OFFSET = 8 * CHECK_SIDE_LENGTH + HALF_CHECK_SIDE_LENGTH;
	BEAROFF_TRAY_LEFT_OFFSET = 16 * CHECK_SIDE_LENGTH + HALF_CHECK_SIDE_LENGTH;

	BEAROFF_TRAY_WIDTH = 2 * CHECK_SIDE_LENGTH;

	BAR_VERT_OFFSET = 7 * CHECK_SIDE_LENGTH;

	BOARD_WIDTH = 18 * CHECK_SIDE_LENGTH;
	BOARD_HEIGHT = CHECK_SIDE_LENGTH * 13+ CHECK_SIDE_LENGTH * 2 / 3;

	FIRST_DIE_LEFT_OFFSET = 10 * CHECK_SIDE_LENGTH + 
	   		3 * CHECK_SIDE_LENGTH - DIE_SIDE_LENGTH - DICE_MARGIN;
	SECOND_DIE_LEFT_OFFSET = FIRST_DIE_LEFT_OFFSET + DIE_SIDE_LENGTH + 2 * DICE_MARGIN;
	DICE_LEFT_OFFSETS = [FIRST_DIE_LEFT_OFFSET, SECOND_DIE_LEFT_OFFSET];

	OFFERED_CUBE_LEFT_OFFSET = 10 * CHECK_SIDE_LENGTH + 3 * CHECK_SIDE_LENGTH -
	   							HALF_CHECK_SIDE_LENGTH + CHECK_SIDE_LENGTH / 12;

	DICE_TOP_OFFSET = BOARD_HEIGHT / 2 - DIE_SIDE_LENGTH / 2;

	CENTERED_CUBE_TOP_OFFSET = DICE_TOP_OFFSET + 2;
	CENTERED_CUBE_LEFT_OFFSET = CHECK_SIDE_LENGTH / 2;

	OVERFLOW_LABEL_OFFSET = CHECK_SIDE_LENGTH / 6;

	CUBE_LEFT_OFFSET = BEAROFF_TRAY_WIDTH / 4;

	NUMBERS_ROW_HEIGHT = CHECK_SIDE_LENGTH / 2;

	POINT_HEIGHT = POINT_CAPACITY * CHECK_SIDE_LENGTH;

	CUBE_TEXT_SIZE = HALF_CHECK_SIDE_LENGTH + HALF_CHECK_SIDE_LENGTH / 2;

	CUBE_OVERFLOW_LABEL_OFFSET = CHECK_SIDE_LENGTH / 24;

}

setDimensions();

var TOP_PLAYER_HAS_CUBE = 1;
var BOTTOM_PLAYER_HAS_CUBE = 2;
var CENTERED_CUBE = 0;
var TOP_PLAYER_OFFERS_CUBE = 3;
var BOTTOM_PLAYER_OFFERS_CUBE = 4;

var BAR_INDEX = -1;
var OFF_INDEX = 0;

var gnuId;
var diceInverted = false;
var submitCalled = false;

var DOUBLE_OR_ROLL_DECISION = 'DOUBLE_OR_ROLL_DECISION';
var TAKE_OR_DROP_DECISION = 'TAKE_OR_DROP_DECISION';

var diceOutcomes = [
	'1-1', '2-1', '2-2', '3-1', '3-2', '3-3',
	'4-1', '4-2', '4-3', '4-4', '5-1', '5-2',
	'5-3', '5-4', '5-5', '6-1', '6-2', '6-3',
	'6-4', '6-5', '6-6'
];

var arrPoints, arrPointsBak;
var arrCheckers;
var arrBar, arrBarBak;
var intOnRoll;
var intDice;
var strDice;
var intCubePos;
var intCubeVal;
var intMatchLgh;
var intScoreW;
var intScoreB;
var booCrawW;
var booCrawB;
var booCrawford;
var isCrawford;
var strReply;
var strMessage;
var intRestOnroll;
var intRestDice;
var intRestCpos;
var intRestCval;
var intRestMlgh;
var intRestWscr;
var intRestBscr;
var numbersPlayed;
var decisionStatus;
var movePairs;

/* board data */
function initData() {
	 arrPoints = new Array(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
	 arrCheckers = new Array(0, 0);
	 arrBar = new Array(0, 0);
	 intOnRoll = 0;
	 intDice = 0;
	 strDice;
	 intCubePos = 0;
	 intCubeVal = 0;
	 intMatchLgh = 0;
	 intScoreW = 0;
	 intScoreB = 0;
	 booCrawW = false;
	 booCrawB = false;
	 booCrawford = false;
	 isCrawford;
	 strReply = "";
	 strMessage = "";
	 intRestOnroll = 0;
	 intRestDice = 0;
	 intRestCpos = 0;
	 intRestCval = 0;
	 intRestMlgh = 0;
	 intRestWscr = 0;
	 intRestBscr = 0;
	 numbersPlayed = [ ]
	 decisionStatus = null;
	 movePairs = [];
}


/* draw data */
var strImageDir = "/static/cacheable/";
var strImageType = ".png";
var intImageOffset = 0;
var boardImages;
var leftBoard;
var ptsOrdered;
var checkerImageUrls = ['checkers/' + prefs['oppt_checker'], 'checkers/' + prefs['plr_checker']];

function escapeRegExp(string){
  return string.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1");
}

function resizeImg(img, mplier) {
	var width = parseInt(img.width, 10);
	var height = parseInt(img.height, 10);
	img.width = (width * mplier);
	img.height = (height * mplier);
}

function initGraphics() {
	var numbers = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15];
	for (var i = 0; i < numbers.length; i++) {
		var img = new Image();
		img.src = strImageDir + 'number' + numbers[i] + '.png';
		img.width = CHECK_SIDE_LENGTH + '';
		img.height = CHECK_SIDE_LENGTH + '';
	}
	var img = new Image();
	img.src = '/static/cacheable/loading.gif';
}

function triggerClickToChecker(pointClicked) {
	$('img.pointi' + (pointClicked == BAR_INDEX ? 24 : (24 - pointClicked))).eq(0).trigger('click');
}

function boardClickHandler(ev) {
	var clickCoords = [ev.clientX, ev.clientY];
	var boardCoords = [$(ev.target).offset().left, $(ev.target).offset().top];
	var relativeCoords = [clickCoords[0] - boardCoords[0], clickCoords[1] - boardCoords[1]];
	var relx = relativeCoords[0], rely = relativeCoords[1];

	var serialIndex;

	var pointsLeft = relx / CHECK_SIDE_LENGTH;
	var isClickOnTopHalf = rely < (BOARD_HEIGHT / 2);

	var pointClicked;

	if (pointsLeft > 8 && pointsLeft < 10) {
		pointClicked = BAR_INDEX;
	}
	else if (pointsLeft > 2 && pointsLeft < 8) {
		pointClicked = Math.floor(pointsLeft) + 1 - 2;
	}
	else if (pointsLeft > 10 && pointsLeft < 16) {
		pointClicked = Math.floor(pointsLeft) + 1 - 2 - 2;
	}

	if (pointClicked != BAR_INDEX) {
		if (isClickOnTopHalf) {
			pointClicked = 12 + pointClicked;
		}
		else {
			pointClicked = 13 - pointClicked;
		}
	}

	triggerClickToChecker(pointClicked);


}

function comparePoint(a, b) {
	if (a == BAR_INDEX) return 1;
	if (b == BAR_INDEX) return -1;
	return a - b;
}

function comparePairs(pairA, pairB) {
	var firstCompare = comparePoint(pairA[0], pairB[0]);
	if (firstCompare != 0) {
		return firstCompare;
	}
	var secondCompare = comparePoint(pairA[1], pairB[1]);
	return secondCompare;
}

function addToMovePairs(pair) {
	$('#move').empty();
	movePairs.push(pair);
	movePairs.sort(comparePairs);
}

function pairElementToHumanReadable(pairEl) {
	if (pairEl == BAR_INDEX) {
		return 'bar';
	}
	if (pairEl > 23) {
		return 'off';
	}
	else {
		return '' + (24 - pairEl);
	}
}

function comparePoints(pointA, pointB) {
	return pointA - pointB;
}

function comparePairs(pairA, pairB) {
	var first = comparePoints(pairA[0], pairB[0]);
	if (first != 0) {
		return first;
	}
	else {
		var second = comparePoints(pairA[1], pairB[1]);
		return second;
	}
}

function formatPoint(point) {
	if (point == BAR_INDEX) {
		return 'bar';
	}
	if (point <= 23) {
		return '' + (24 - point);
	}
	return 'off';
}

function formatPair(pair) {
	var s = '';
	s += formatPoint(pair[0]);
	s += '/';
	s += formatPoint(pair[1]);
	s += pair[2] ? '*' : '';
	return s;
}

function popPairStartingWith(movePairs, w) {
	for (var pairi = 0; pairi < movePairs.length; pairi++) {
		if (movePairs[pairi][0] == w) {
			return movePairs.splice(pairi, 1)[0];
		}
	}
}

function popPairEndingWith(movePairs, w) {
	for (var pairi = 0; pairi < movePairs.length; pairi++) {
		if (movePairs[pairi][1] == w) {
			return movePairs.splice(pairi, 1)[0];
		}
	}
}

function repeat(s, n, d){
	var a = [];
	while(a.length < n){
		a.push(s);
	}
	return a.join(d);
}

function movePairsToMoveString() {
	var pairStartingWith, pairEndingWith, endingPairWrittenForHit;
	var resultString = '';
	var movePairsLocal = movePairs.slice();
	if (movePairsLocal && movePairsLocal.length > 0) {
		for (var pointi = BAR_INDEX; pointi < 24; pointi++) {
			while (pairStartingWith = popPairStartingWith(movePairsLocal, pointi)) {
				// For each pair that starts with pointi.
				resultString += formatPoint(pointi);
				// Find what the ending point is.
				var endingPair = pairStartingWith;
				while (true) {
					if (arrPointsBak[endingPair[1]] == 1 
							&& (
								!endingPairWrittenForHit ||
								endingPair[0] == endingPairWrittenForHit[0] && endingPair[1] == endingPairWrittenForHit[1] ||
								endingPair[1] != endingPairWrittenForHit[1]
								)
							) {
						resultString += '/';
						resultString += formatPoint(endingPair[1]);
						resultString += '*';
						endingPairWrittenForHit = endingPair;
					}
					var candidate = popPairStartingWith(movePairsLocal, endingPair[1]);
					if (!candidate) { break; }
					endingPair = candidate;
				}
				if (endingPair !== endingPairWrittenForHit) {
					resultString += '/';
					resultString += formatPoint(endingPair[1]);
				}
				resultString += ' ';
			}
		}
	}
	resultString = resultString.trim();
	var elements = resultString.split(' ');
	for (var elemi = 0; elemi < elements.length; elemi++) {
		var element = elements[elemi];
		for (var repi = 4; repi >= 2; repi--) {
			resultString = resultString.replace(
					RegExp('\\b' + escapeRegExp(repeat('' + element + '', repi, ' ')) + '(?=( |$))'), element + '(' + repi + ')'
			);
		}
	}

	/* The following code fixes some cases where there appears that there is a
	 * second hit on the same point. For example, see the gnuid
	 * bBthChKwbXAwUA:8ImkAAAAIAAE , in which without the code that follows, we
	 * would have a move string of bar/24 6/4* 5/4* .
	 */
	var mo, secondHitShownRegex = /^(.*)(\/\d+\*)(.*?)(\2)(.*)$/;
	while (mo = secondHitShownRegex.exec(resultString)) {
		var newResultString = '';
		for (var groupi = 1; groupi < mo.length; groupi++) {
			newResultString += mo[groupi];
			if (groupi == 4) {
				/* Remove the second asterisk. */
				newResultString = newResultString.substring(0, newResultString.length - 1);
			}
		}
		resultString = newResultString;
	}
	/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

	return resultString.trim();
}

function sumOfCheckersInFirstNPositions(n) {
	var s = arrBar[WHITE_PLAYER];
	for (var i = 0; i < n; i++) {
		if (arrPoints[i] < 0) {
			s += -arrPoints[i];
		}
	}
	return s;
}

function numbersToPlay() {

	var arrDice = strDice.split('-');
	if (diceInverted) {
		arrDice.reverse();
	}
	for (var i = 0; i < arrDice.length; i++) {
		arrDice[i] = parseInt(arrDice[i], 10);
	}
	var toPlay = arrDice.slice(); // Copy.
	if (toPlay[0] == toPlay[1]) {
		toPlay.push(toPlay[0]);
		toPlay.push(toPlay[0]);
	}
	for (var i = 0; i < numbersPlayed.length; i++) {
		var inof = toPlay.indexOf(numbersPlayed[i]);
		if (inof != -1) {
			toPlay.splice(inof, 1);
		}
	}
	return toPlay;

}

function isCheckerDecision() {
	return (decisionStatus != DOUBLE_OR_ROLL_DECISION && decisionStatus != TAKE_OR_DROP_DECISION);
}

function areThereLegalMoves(numbersToPlayIn) {
	if (numbersToPlayIn == null) {
		numbersToPlayIn = numbersToPlay();
	}
	if (arrBar[WHITE_PLAYER] > 0) {
		for (var numi = 0; numi < (numbersToPlayIn).length; numi++) {
			var number = (numbersToPlayIn)[numi];
			if (arrPoints[number - 1] < 2) {
				return true;
			}
		}
	}
	else {
		for (var numi = 0; numi < (numbersToPlayIn).length; numi++) {
			for (var src = 0; src < arrPoints.length; src++) {
				if (arrPoints[src] < 0) {
					var dst = src + (numbersToPlayIn)[numi];
					if (
							sumOfCheckersInFirstNPositions(18) == 0 && 
								(dst == 24 || sumOfCheckersInFirstNPositions(src) == 0 && dst > 24)
							||
							dst < 24 && arrPoints[dst] < 2
					) {
						return true;
					}
				}
			}
		}
	}
	return false;
}

function drawDice() {
	boardImageWrapper.find('img.die').remove();
	if (strDice != '11' && strDice != '10') {
		var arrDice = strDice.split('-');
		if (diceInverted) {
			arrDice.reverse();
		}
		for (var i = 0; i < arrDice.length; i++) {
			arrDice[i] = parseInt(arrDice[i], 10);
			if (arrDice[i] >= 1 && arrDice[i] <= 6) {
				var img = new Image();
				img.src = strImageDir + 'die' + arrDice[i] + '.png';
				img.width = DIE_SIDE_LENGTH + '';
				img.height = DIE_SIDE_LENGTH + '';
				$(img).css('position', 'absolute')
					.css('left', DICE_LEFT_OFFSETS[i] + 'px')
					.css('top', DICE_TOP_OFFSET + 'px')
					.addClass('die')
					.addClass('die' + arrDice[i])
					.data('value', parseInt(arrDice[i], 10))
				boardImageWrapper.append(img);
			}
		}
	}

}

function pipCountWhite() {
    var a = 0;
    for (i = 0; i < 24; i++) {
        if (arrPoints[i] > 0) {
            a += (i + 1) * arrPoints[i]
        }
    }
    a += 25 * arrBar[0];
    return a
}

function pipCountBlue() {
    var a = 0;
    for (i = 0; i < 24; i++) {
        if (arrPoints[i] < 0) {
            a += (24 - i) * Math.abs(arrPoints[i])
        }
    }
    a += 25 * arrBar[1];
    return a
}

function formatDice(a) {
    return a.toString().substring(0, 1) + "" + a.toString().substring(1, 2)
}

function replaceString(a, b, e) {
    for (var d = 0; d < e.length; d++) {
        if (e.substring(d, d + a.length) == a) {
            e = e.substring(0, d) + b + e.substring(d + a.length, e.length)
        }
    }
    return e
}

function posIDBits() {
    var a = 0;
    var d = "";
    var b = "";
    for (a = 0; a <= 23; a++) {
        if (arrPoints[a] > 0) {
            for (j = 0; j < arrPoints[a]; j++) {
                d += "1"
            }
        }
        d += "0"
    }
    for (a = 0; a < arrBar[1]; a++) {
        d += "1"
    }
    d += "0";
    for (a = 23; a >= 0; a--) {
        if (arrPoints[a] < 0) {
            for (j = 0; j < (-arrPoints[a]); j++) {
                b += "1"
            }
        }
        b += "0"
    }
    for (a = 0; a < arrBar[0]; a++) {
        b += "1"
    }
    b += "0";
    d += b;
    for (a = d.length; a < 80; a++) {
        d += "0"
    }
    return d
}

function matchIDBits() {
    var a = "";
    a += pad(rev((intCubeVal == 1) ? 0 : dec2Bin(dec2Bin(intCubeVal).length - 1)), 4);
    a += (intCubePos === 0) ? "11" : ((intCubePos == 1) ? "00" : "10");
    a += intOnRoll;
    a += (booCrawW || booCrawB) ? "1" : "0";
    a += "100";
    a += intOnRoll;
    a += "0";
    a += "00";
    if (intDice !== 0) {
        a += pad(rev(dec2Bin(intDice % 10)), 3) + pad(rev(dec2Bin(Math.floor(intDice / 10))), 3)
    } else {
        a += "000000"
    }
    a += pad(rev(dec2Bin(intMatchLgh)), 15);
    a += pad(rev(dec2Bin(intScoreW)), 15);
    a += pad(rev(dec2Bin(intScoreB)), 15);
    return a
}

function bin2Dec(e) {
    var b = 0;
    for (var d = 0; d < e.length; d++) {
        b = b * 2;
        if (e.charAt(d) == "1") {
            b = b + 1
        }
    }
    return b
}

function rev(d) {
    var a = "";
    for (var b = d.length - 1; b >= 0; b--) {
        a += d.charAt(b)
    }
    return a
}

function bin2base64(e) {
    var b = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    var f = "";
    var a = "";
    e = pad(e, 8);
    for (var d = 0; d < (e.length / 8); d++) {
        f += rev(e.substring(d * 8, (d + 1) * 8))
    }
    f = pad(f, 6);
    for (d = 0; d < (f.length / 6); d++) {
        a += b.charAt(bin2Dec(f.substring(d * 6, (d + 1) * 6)))
    }
    return a
}

function base642bin(f) {
    var b = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    var e = "";
    var a = "";
    for (var d = 0; d < f.length; d++) {
        e += rev(pad(rev(dec2Bin(b.indexOf(f.charAt(d)))), 6))
    }
    e = pad(e, 8);
    for (d = 0; d < (e.length / 8); d++) {
        a += rev(e.substring(d * 8, (d + 1) * 8))
    }
    return a
}

function pad(d, a) {
    if (d === "") {
        d = "0"
    }
    for (var b = 0; b < (d.length % a); b++) {
        d += "0"
    }
    return d
}

function gnubgID() {
    return bin2base64(posIDBits())
}

function gnuMatchID() {
    return bin2base64(matchIDBits())
}


function setDataFromGnuId(gnuId) {
	initData();
    strMessage = "Invalid Position or Match ID";

    var strGnuId = gnuId.split(':')[0];
    strGnuId = replaceString(" ", "+", strGnuId);

    var strMatchId = gnuId.split(':')[1];
    strMatchId = replaceString(" ", "+", strMatchId);

    var positionIdDecoded = base642bin(strGnuId);
    var matchIdDecoded = base642bin(strMatchId);

    var p = 0;
    var h = 0;
    var f = 0;
    var e = 15;
    for (var m = 0; m <= 23; m++) {
        h = 0;
        while (positionIdDecoded.charAt(p) == "1") {
            if (m < 12) {
                f = m
            } else {
                f = 35 - m
            }
            h++;
            e--;
            p++
        }
        p++;
        if (h > 0) {
			arrPoints[m] = h;
        }
    }
    h = 0;
    while (positionIdDecoded.charAt(p) == "1") {
        h++;
        e--;
        p++
    }
    p++;
	arrBar[0] = h;
    if (e < 0) {
        return false
    }
    e = 15;
    for (m = 23; m >= 0; m--) {
        h = 0;
        while (positionIdDecoded.charAt(p) == "1") {
            if (m < 12) {
                f = m
            } else {
                f = 35 - m
            } 
            h++;
            e--;
            p++
        }
        p++;
        if (h > 0) {
			arrPoints[m] = -h;
        }
    }
    h = 0;
    while (positionIdDecoded.charAt(p) == "1") {
        h++;
        e--;
        p++
    }
	arrBar[1] = h;
    if (e < 0) {
        return false
    }
    intCubeVal = Math.pow(2, parseInt(bin2Dec(rev(matchIdDecoded.substring(0, 4))), 10));
    var o = matchIdDecoded.substring(4, 6);
    m = (o == "11") ? 0 : ((o == "00") ? 1 : 2);
    var b = matchIdDecoded.substring(6, 7);
    if (b === 0 && m == 1) {
        m = 2;
		intCubePos = m;
    } else {
        if (b === 0 && m == 2) {
            m = 1;
			intCubePos = m;
        } else {
			intCubePos = m;
        }
    }
    m = matchIdDecoded.substring(6, 7);
    if (m === 0) {
        m = 1;
		intOnRoll = m;
    } else {
		intOnRoll = m;
    }
    var n = bin2Dec(rev(matchIdDecoded.substring(15, 18)));
    var l = bin2Dec(rev(matchIdDecoded.substring(18, 21)));
    if (n > 0 && l > 0) {
        o = (n < l) ? l + "-" + n : n + "-" + l;
		intDice = diceOutcomes.indexOf(o);
    } else {
		intDice = 0;
		if (matchIdDecoded.substring(12, 13) == '1') {
			decisionStatus = TAKE_OR_DROP_DECISION;
		}
		else {
			decisionStatus = DOUBLE_OR_ROLL_DECISION;
		}
    }
	strDice = o;
    m = bin2Dec(rev(matchIdDecoded.substring(21, 36)));
	intMatchLgh = m;
    intScoreW = bin2Dec(rev(matchIdDecoded.substring(36, 51)));
    if (intScoreW > 24) {
        intScoreW = 0
    }
    intScoreB = bin2Dec(rev(matchIdDecoded.substring(51, 66)));
    if (intScoreB > 24) {
        intScoreB = 0
    }
    m = matchIdDecoded.substring(6, 7);
    booCrawford = matchIdDecoded.substring(7, 8);
    if (booCrawford == 1) {
        booCrawford = "true"
        isCrawford = true
    } else {
        booCrawford = "false"
        isCrawford = false
    } 
    var r = bin2Dec(rev(matchIdDecoded.substring(11, 12)));
    var q = bin2Dec(rev(matchIdDecoded.substring(6, 7)));
    if (r != q) {
        var d = bin2Dec(rev(matchIdDecoded.substring(0, 4)));
        d = (d + 1);
		intCubeVal = Math.pow(2, d);
        if (r == "0") {
			intCubePos = 4;
        } else {
            if (r == "1") {
				intCubePos = 3;
            }
        }
    }
    strMessage = "";

	if (matchIdDecoded.substring(6, 7) == '0') {
		arrPoints.reverse();
		for (var arrPointi = 0; arrPointi < arrPoints.length; arrPointi++) {
			arrPoints[arrPointi] = -arrPoints[arrPointi];
		}
		arrBar.reverse();
	}

	arrPointsBak = arrPoints.slice();
	arrBarBak = arrBar.slice();
    return true
}

function dec2Bin(b) {
    var a = "";
    if (b === 0) {
        a = "0"
    }
    while (b > 0) {
        if (b % 2 == 1) {
            a = "1" + a
        } else {
            a = "0" + a
        }
        b = Math.floor(b / 2)
    }
    return a
}

function clearBoard() {
	$('#match_score table td').remove();
	boardImageWrapper.find('> img').slice(1).remove();
}


function pointiToLeftOffset(pointi) {
	var leftOffsetInWidths = 2; // 2 for the left bearoff tray
	if (pointi <= 11) {
		leftOffsetInWidths += 11 - pointi;
		if (pointi <= 5) {
			leftOffsetInWidths += 2; // 2 for the bar
		}
	}
	else {
		leftOffsetInWidths += pointi - 12;
		if (pointi >= 18) {
			leftOffsetInWidths += 2; // 2 for the bar
		}
	}

	return leftOffsetInWidths * CHECK_SIDE_LENGTH;
}

function pointiCheckeriToVerticalOffset(pointi, checkeri) {
	var checkeriModified = checkeri > POINT_CAPACITY - 1 ?
				POINT_CAPACITY - 1 : checkeri;
	var offset = NUMBERS_ROW_HEIGHT;
	var type;
	if (pointi > 11) {
		type = 'bottom';
	}
	else {
		type = 'top';
	}
	offset += checkeriModified * CHECK_SIDE_LENGTH;
	return [type, offset];
}

function checkerClickHandler(ev) {

	var moveMade = false;
	var numi = -1;
	/* Keeping the three state variables that are possibly modified by this
	 * method, in case they have to be restored. This restoration only
	 * needs to happen when the player tries to play a die even though this
	 * prevents him from playing a larger die. */
	var arrPointsBak = arrPoints.slice();
	var arrBarBak = arrBar.slice();
	var numbersPlayedBak = numbersPlayed.slice();

	function checkIfLargerDieCanBePlayed() {
		var played = numbersPlayed[numbersPlayed.length - 1];
		var largerFound = false;
		for (var i = 0; i < (numbersToPlay()).length; i++) {
			if ((numbersToPlay())[i] > played) {
				largerFound = true;
				break;
			}
		}
		if (largerFound) {
			if (!areThereLegalMoves()) {
				return false;
			}
		}
		return true;
	}

	function restoreState() {
		arrPoints = arrPointsBak;
		arrBar = arrBarBak;
		numbersPlayed = numbersPlayedBak;
	}

	var numsToPlay = numbersToPlay();
	if (numsToPlay.length == 2) {
		if (numsToPlay[0] != numsToPlay[1]) {
			var largeDieCanBePlayedAtStart = 
				areThereLegalMoves([Math.max(numsToPlay[0], numsToPlay[1])]);
		}
	}

	while (true) {
		numi += 1;
		var dieValue = (numbersToPlay())[numi];
		if (dieValue) {
			var src = $(ev.target).data('pointi');
			var dst = src + dieValue;
			if (src != BAR_INDEX && arrBar[WHITE_PLAYER] == 0 || src == BAR_INDEX) {
				if (dst <= 23) {
					if (arrPoints[dst] <= 1) {
						if (src != BAR_INDEX) {
							arrPoints[src] += 1;
						}
						else {
							arrBar[WHITE_PLAYER] -= 1;
						}
						var wasHit = (arrPoints[dst] == 1);
						if (wasHit) {
							arrPoints[dst] -= 1;
							arrBar[RED_PLAYER] += 1;
						}
						arrPoints[dst] -= 1;
						numbersPlayed.push(dieValue);
						var canLargerDieBePlayed = checkIfLargerDieCanBePlayed();
						if (canLargerDieBePlayed || !largeDieCanBePlayedAtStart) {
							addToMovePairs([src, dst, null]);
							drawBoard();
							break;
						}
						else {
							restoreState();
						}
					}
				}
				else { // dst is > 23
					if (sumOfCheckersInFirstNPositions(18) == 0) {
						// Bearoff
						if (dst == 24 || sumOfCheckersInFirstNPositions(src) == 0) {
							arrPoints[src] += 1;
							numbersPlayed.push(dieValue);
							var canLargerDieBePlayed = checkIfLargerDieCanBePlayed();
							if (canLargerDieBePlayed || !largeDieCanBePlayedAtStart) {
								addToMovePairs([src, dst]);
								drawBoard();
								break;
							}
							else {
								restoreState();
							}
						}
					}
				}
			}
		}
		else {
			break;
		}
	}
}


function setBoardClickHandlers() {

	/* We never need to remove click handlers because the elements to which
	 * they are attached are new elements, created each time we call the
	 * drawBoard function. */
	if (isCheckerDecision() && !submitCalled && !isAnalysisShown()) {
		$('img.white_checker').click(checkerClickHandler);
	}
}

function drawBoard() {

	var toAppend = [ ];
	function appendImgForOverCheckers() {
		if (checkeri >= POINT_CAPACITY + 1) {
			var imgOverflow = new Image;
			imgOverflow.src = strImageDir + 'number' + checkeri + '.png';
			imgOverflow.width = CHECK_SIDE_LENGTH + '';
			imgOverflow.height = CHECK_SIDE_LENGTH + '';
			$(imgOverflow).css('position', 'absolute')
				.css('width', OVERFLOW_INDICATOR_SIZE + 'px')
				.css('height', OVERFLOW_INDICATOR_SIZE + 'px')
				.css(
					'left', 
					parseInt($(img).css('left'), 10) + 
					(CHECK_SIDE_LENGTH - OVERFLOW_INDICATOR_SIZE) / 2 + 
					'px'
				)
				.css(
					vertOffset[0], 
					vertOffset[1] + 
					(CHECK_SIDE_LENGTH - OVERFLOW_INDICATOR_SIZE) / 2 + 
					'px'
				)
				.addClass('overflow_indicator')
				.addClass(playeri == 1 ? 'white_checker' : 'red_checker')
				.addClass('checker')
				.addClass('pointi' + pointi)
				.data('pointi', pointi)
			;
			toAppend.push(imgOverflow);
		}
	}

	clearBoard();

	var checkersOff = [15, 15];
	for (var pointi = 0; pointi < 24; pointi++) {

		var encodedCheckers, numOfCheckers;
		encodedCheckers = arrPoints[pointi];
		numOfCheckers = Math.abs(encodedCheckers);

		if (numOfCheckers != 0) {
			var checkeri;
			for (checkeri = 0; checkeri < numOfCheckers; checkeri++) {
				var img = new Image();
				var playeri = arrPoints[pointi] > 0 ? RED_PLAYER : WHITE_PLAYER;
				var vertOffset = pointiCheckeriToVerticalOffset(pointi, checkeri);
				img.src = strImageDir + checkerImageUrls[playeri];
				img.width = CHECK_SIDE_LENGTH + '';
				img.height = CHECK_SIDE_LENGTH + '';
				$(img).css('position', 'absolute')
					.css('left', pointiToLeftOffset(pointi) + 'px')
					.css(vertOffset[0], vertOffset[1] + 'px')
					.addClass(playeri == 1 ? 'white_checker' : 'red_checker')
					.addClass('checker')
					.addClass('pointi' + pointi)
					.data('pointi', pointi)
				toAppend.push(img);
				checkersOff[playeri] -= 1;
			}
			appendImgForOverCheckers();
		}
	}

	for (playeri = 0; playeri < 2; playeri++) {
		var numOfCheckers = arrBar[playeri];
		var checkeri;
		for (checkeri = 0; checkeri < numOfCheckers; checkeri++) {
			var img = new Image();
			img.src = strImageDir + checkerImageUrls[playeri];
			img.width = CHECK_SIDE_LENGTH + '';
			img.height = CHECK_SIDE_LENGTH + '';
			var vertOffset = pointiCheckeriToVerticalOffset(
					playeri == RED_PLAYER ? 0 : 23,
					checkeri
			);
			$(img).css('position', 'absolute')
				.css('left', BAR_LEFT_OFFSET + 'px')
				.css( vertOffset[0], vertOffset[1] + BAR_VERT_OFFSET + 'px')
				.addClass(playeri == 1 ? 'white_checker' : 'red_checker')
				.addClass('checker')
				.addClass('pointi' + pointi)
				.data('pointi', BAR_INDEX)
			toAppend.push(img);
			checkersOff[playeri] -= 1;
		}
		appendImgForOverCheckers();
	}

	for (playeri = 0; playeri < 2; playeri++) {
		var numOfCheckers = checkersOff[playeri];
		var checkeri;
		for (checkeri = 0; checkeri < numOfCheckers; checkeri++) {
			var img = new Image();
			img.src = strImageDir + checkerImageUrls[playeri];
			img.width = CHECK_SIDE_LENGTH + '';
			img.height = CHECK_SIDE_LENGTH + '';
			var vertOffset = pointiCheckeriToVerticalOffset(
					playeri == RED_PLAYER ? 0 : 23,
					checkeri
			);
			$(img).css('position', 'absolute')
				.css('left', BEAROFF_TRAY_LEFT_OFFSET + 'px')
				.css( vertOffset[0], vertOffset[1] + 'px')
				.addClass(playeri == 1 ? 'white_checker' : 'red_checker')
				.addClass('checker');
			toAppend.push(img);
		}
		appendImgForOverCheckers();
	}

	drawDice();

	if (!isCrawford) {
		var img_blank = new Image();
		img_blank.src = strImageDir + 'cube_blank.png';
		img_blank.width = CHECK_SIDE_LENGTH + '';
		img_blank.height = CHECK_SIDE_LENGTH + '';
		var img_number = new Image();

		$(img_blank).addClass('cube');
		$(img_number).addClass('number');

		var img = $(img_blank).add(img_number);
		img.css('position', 'absolute');

		if (intCubePos == CENTERED_CUBE) {
			img.css('top', CENTERED_CUBE_TOP_OFFSET + 'px');
		}
		else if (intCubePos == TOP_PLAYER_HAS_CUBE) {
			img.css('top', NUMBERS_ROW_HEIGHT + 'px');
		}
		else if (intCubePos == BOTTOM_PLAYER_HAS_CUBE) {
			img.css('bottom', NUMBERS_ROW_HEIGHT + 'px');
		}
		else if (intCubePos == TOP_PLAYER_OFFERS_CUBE) {
			img.css('top', DICE_TOP_OFFSET + 'px');
		}
		else if (intCubePos == BOTTOM_PLAYER_OFFERS_CUBE) {
			img.css('top', DICE_TOP_OFFSET + 'px');
		}

		if (intCubePos == TOP_PLAYER_HAS_CUBE || intCubePos == BOTTOM_PLAYER_HAS_CUBE) {
			img.css('left', CUBE_LEFT_OFFSET + 'px');
		}
		else if (intCubePos == TOP_PLAYER_OFFERS_CUBE 
					|| intCubePos == BOTTOM_PLAYER_OFFERS_CUBE) {
			img.css('left', OFFERED_CUBE_LEFT_OFFSET + 'px');
		}
		else if (intCubePos == CENTERED_CUBE) {
			img.css('left', CENTERED_CUBE_LEFT_OFFSET);
		}

		for (var imgi = 0; imgi < img.length; imgi++) {
			toAppend.push(img[imgi]);
		}

		if (intCubeVal != 1 && (intCubePos == TOP_PLAYER_HAS_CUBE 
							|| intCubePos == BOTTOM_PLAYER_OFFERS_CUBE)) {
				$(img_number).css('transform', 'rotate(180deg)');
				img_number.src = strImageDir + 'number' + intCubeVal + '.png';
				img_number.width = CHECK_SIDE_LENGTH + '';
				img_number.height = CHECK_SIDE_LENGTH + '';
		}
		else if (intCubeVal == 1) {
				$(img_number).css('transform', 'rotate(270deg)');
				img_number.src = strImageDir + 'number64.png';
				img_number.width = CHECK_SIDE_LENGTH + '';
				img_number.height = CHECK_SIDE_LENGTH + '';
		}
		else {
			img_number.src = strImageDir + 'number' + intCubeVal + '.png';
			img_number.width = CHECK_SIDE_LENGTH + '';
			img_number.height = CHECK_SIDE_LENGTH + '';
		}
	}

	boardImageWrapper.append($(toAppend));


	$('#match_score table tr').each(function(elemi, elem) {
		elemi = 1-elemi;
		if (elemi == 1) {
			$('<td>').appendTo(elem)
				.append('Match length: ' + intMatchLgh)
		}
		else if (elemi == 0) {
			$('<td>').appendTo(elem)
				.append(isCrawford ? 'Crawford game' : '')
				.css('font-weight', 'bolder')
		}

		$('<td>').appendTo(elem)
			.append(
				elemi == 0 ? 'You:' : 'Oppt:'
			)

		$('<td>').appendTo(elem)
			.append(
				$('<img>').attr('src', strImageDir + checkerImageUrls[1 - elemi])
			)

		$('<td>').appendTo(elem)
			.append(
				(elemi == 0 ? intScoreB : intScoreW) + ' point(s)'
			)

		var pipsBlue = pipCountBlue();
		var pipsWhite = pipCountWhite();
		var pipsDiff = pipsBlue - pipsWhite;

		$('<td>').appendTo(elem)
			.append(
				(elemi == 0 ? 'pips: ' + pipsBlue + ' (' + (pipsDiff >= 0 ? '+' : '')  + pipsDiff + ')' : '')
			)
				
	});

	setBoardClickHandlers();
	setInvertDisabledness();

	$('#decision_description').empty();

	if (!submitCalled && !isAnalysisShown()) {
		if (isCheckerDecision()) {
			var moveString = movePairsToMoveString();
			var decisionDescription = 
				'Please make checker play on the board. First click plays left die. <p>' + 
				(moveString != null && moveString.length > 0 ? 'Your move: ' : '') + 
				'<span id="move">' + 
				moveString + 
				'</span>'
			;
		}
		else if (decisionStatus == DOUBLE_OR_ROLL_DECISION) {
			var decisionDescription = '';
			decisionDescription += 'Please make cube play: ';
			decisionDescription += '<label for="double_checkbox"><input id="double_checkbox" type="radio" name="cube_decision" value="double">Double</label>';
			decisionDescription += '<label for="roll_checkbox"><input id="roll_checkbox" type="radio" name="cube_decision" value="roll">Roll</label>';
		}
		else if (decisionStatus == TAKE_OR_DROP_DECISION) {
			var decisionDescription = '';
			decisionDescription += 'Please make cube play: ';
			decisionDescription += '<label for="take_checkbox"><input id="take_checkbox" type="radio" name="cube_decision" value="take">Take</label>';
			decisionDescription += '<label for="drop_checkbox"><input id="drop_checkbox" type="radio" name="cube_decision" value="drop">Drop</label>';
		}
		$('#decision_description').append(decisionDescription);
	}


	$('input[name=cube_decision]').click(setSubmitDisabledness);

	setSubmitDisabledness(); // This needs to be after the #move value has been set, since it can possibly use the #move value calculated there.
	setUndoDisabledness();

}

function undo() {
	$('input[name=show_move]').removeAttr('checked');
	readGnuIdAndDraw(gnuId);
}

function setSubmitDisabledness() {
	if (isAnalysisShown()) {
		$('#submit').attr('disabled', 'true');
	}
	else if (isCheckerDecision()) {
		if (!areThereLegalMoves()) {
			if ($('#auto_submit:checked').length == 0) {
				$('#submit').removeAttr('disabled');
			}
			else {
				submitHandler();
			}
		}
		else {
			$('#submit').attr('disabled', 'true');
		}
	}
	else {
		if ($('input[name=cube_decision]:checked').length > 0) {
			if ($('#auto_submit:checked').length == 0) {
				$('#submit').removeAttr('disabled');
			}
			else {
				submitHandler();
			}
		}
		else {
			$('#submit').attr('disabled', 'true');
		}
	}

	setAutoSubmitDisabledness();
}

function setAutoSubmitDisabledness() {
	if (isAnalysisShown()) {
		$('#auto_submit_label').addClass('disabled');
		$('#auto_submit_label input').attr('disabled', 'disabled');
	}
	else {
		$('#auto_submit_label').removeClass('disabled');
		$('#auto_submit_label input').removeAttr('disabled');
	}
}

function getSelectedMove() {
	if (isCheckerDecision()) {
		return $('#move').text();
	}
	else {
		return $('input[name=cube_decision]:checked').attr('value');
	}
}

function setUndoDisabledness() {
	if (isAnalysisShown() || submitCalled && isCheckerDecision()) {
		$('.restore_position').removeAttr('disabled');
		if (!isCheckerDecision()) {
			// This if is to avoid hiding the "Your move" bit. Right now it is
			// placed inside decision_description.
			$('#decision_description').hide();
		}
	}
	else {
		if (isCheckerDecision()) {
			if (numbersPlayed && numbersPlayed.length > 0) {
				$('.undo').removeAttr('disabled');
			}
			else {
				$('.undo').attr('disabled', 'true');
			}
		}
		else {
				$('.undo').attr('disabled', 'true');
		}
	}
}

function setInvertDisabledness() {
	if (isAnalysisShown() || submitCalled) {
		$('#invert_dice').attr('disabled', 'true');
	}
	else {
		if (isCheckerDecision()) {
			if (strDice[0] == strDice[2] || numbersPlayed && numbersPlayed.length > 0) {
				$('#invert_dice').attr('disabled', 'true');
			}
			else {
				$('#invert_dice').removeAttr('disabled');
			}
		}
		else {
				$('#invert_dice').attr('disabled', 'true');
		}
	}
}

function readGnuIdAndDraw(gnuId) {
	setDataFromGnuId(gnuId);
	drawBoard();
}


function reverse(s) {
	return s.split("").reverse().join("");
}

function invertDice() {
	diceInverted = !diceInverted;
	drawDice();
}

function showMoveClickHandler(target) {
	readGnuIdAndDraw(gnuId);
	var move = $(target).parent().parent().parent().find('.move_notation').text();
	var moveSplit = move.split(' ');
	for (var movei = 0; movei < moveSplit.length; movei++ ) {
		var moveSegments = moveSplit[movei].split('/');
		var pointRe = /bar|off|\d+/;
		var repeatRe = /\(([234])\)/;

		var point = pointRe.exec(moveSegments[0])[0];
		var dest = pointRe.exec(moveSegments[moveSegments.length - 1])[0];
		var repeat = repeatRe.exec(moveSegments[moveSegments.length - 1]);

		if (point == 'bar') {
			point = BAR_INDEX;
		}
		else {
			point = parseInt(point, 10);
		}

		if (dest == 'off') {
			dest = OFF_INDEX;
		}
		else {
			dest = parseInt(dest, 10);
		}

		if (repeat) {
			repeat = parseInt(repeat[1], 10);
		}
		else {
			repeat = 1;
		}

		for (var i = 0; i < repeat; i++) {
			if (point == BAR_INDEX) {
				arrBar[WHITE_PLAYER] -= 1;
			}
			else {
				arrPoints[24 - point] += 1;
			}
			if (dest != OFF_INDEX) {
				arrPoints[24 - dest] -= 1;
			}
		}

		var hitRe = /(\d+)\*/g;

		while (true) {
			var moHit = hitRe.exec(moveSplit[movei]);
			if (moHit == null) break;

			var hitPoint = parseInt(moHit[1], 10);

			arrPoints[24 - hitPoint] -= 1;
			arrBar[RED_PLAYER] += 1;
		}

	}

	drawBoard();
}

function drawMoves(dataReturned) {
	var scrollTop = $(window).scrollTop();
	var movesColumn = $('#moves_column');
	movesColumn.append(dataReturned['moves_html']);
	$('.restore_position').click(function(ev) {
		undo();
	});
	$(window).scrollTop(scrollTop);
	drawComments(dataReturned);
}

function drawComments(dataReturned) {
	$('#comments').empty()
		.append(dataReturned['comments_html'])
	;
}

function drawNextPositionButton() {
	$('#submit').hide();
	$('#next_position').show();
	$('#similar_pos_label').show();
	$('.position_types_allowed').show();
}

function getParameterValue(parameter, s) {
	var mo = (new RegExp("[?#&]" + parameter + "=(.*?)(&|$)")).exec(s);
	if (mo && mo[1]) {
		return decodeURIComponent(mo[1]);
	}
	return null;
}

function showLoading(className, whereFunction) {
	if ($('.' + className).length == 0) {
		whereFunction(
			$('<span class="loading_indicator"><img src="/static/cacheable/loading.gif"></span>').addClass(className)
		);
	}
}

function removeLoading(className) {
	$('.' + className).remove();
}

function isAnalysisShown() {
	var result = $('#moves_table').length > 0;
	return result;
}

function submitHandler(ev) {

	if (submitCalled) return;
	submitCalled = true;
	setUndoDisabledness();

	$('img.white_checker, #board').off();

	$('#submit').attr('disabled', 'true');
	$('.undo').attr('disabled', 'true');
	$('#invert_dice').attr('disabled', 'true');
	showLoading(
			'submit_loading_indicator', 
			function (content) {
				$('#next_position, #submit').eq(-1).after(content);
			}
	);
	$.ajax(
		'submit',
		{
			data: {
				gnuid: gnuId
				,move: getSelectedMove()
				,d: Math.random()
			}
			,type: 'POST'
			,success: function(dataReturned) {
				drawMoves(dataReturned);
				drawNextPositionButton();
				{
					var jqRating = $('#rating');
					var jqPlayedCount = $('#played_count');
					var newRating = dataReturned['player_rating'];
					if (newRating != null) {
						/* If there is a logged in player. */
						var oldRating = parseFloat(jqRating.text());
						var oldCount = parseInt(jqPlayedCount.text(), 10);
						var diff = newRating - oldRating;

						jqRating.text(newRating.toFixed(2));
						$('<span id="rating_diff">').appendTo(jqRating)
							.addClass(diff > 0 ? 'positive_diff' : diff == 0 ? 'no_diff' : 'negative_diff')
							.text(' (' + (diff >= 0 ? '+' : '') + diff.toFixed(2) + ')')
						;

						jqPlayedCount.text(oldCount + 1);

					}
				}
				removeLoading('submit_loading_indicator');
				setUndoDisabledness();
			}
		}
	);
}

function postComment() {
	var jq = $('textarea[name=body]')
	var body = jq.val();
	jq.val('');
	showLoading(
			'comment_loading_indicator', 
			function(content) {
				$('#add_a_comment_header').before(content);
			}
	);
	$.ajax(
			'postcomment',
			{
				data: {
					gnuid: gnuId
					,body: body
				}
				,success: function(dataReturned) {
					drawComments({comments_html: dataReturned['comments_html']});
					removeLoading('comment_loading_indicator');
					location.hash = $('.comment_box').eq(-1).attr('id');
				}
				,type: 'POST'
			}
	);
}

function showReportPosition() {
	$('#report_position_success').hide();
	/* TODO: focus doesn't seem to work in firefox and IE, but it does work in Chrome. */
	$('div.report_position').show().find('textarea').focus();
}

function reportPosition() {
	var jq = $('textarea.report_position');
	var body = jq.val();
	jq.val('');
	showLoading(
			'report_position_loading_indicator', 
			function(content) {
				$('#report_position_div').before(content);
			}
	);
	$.ajax(
			'postreport',
			{
				data: {
					gnuid: gnuId
					,body: body
				}
				,success: function(dataReturned) {
					removeLoading('report_position_loading_indicator');
					$('#report_position_div').hide().after(
						'<div class="success" id="report_position_success">Position reported successfully. Thank you for taking the time to do so!</div>'
					);
				}
				,type: 'POST'
			}
	);
}

function checkboxHandler(id) {
	document.cookie = id + '=' + ($('#' + id + ':checked').length > 0 ? 'true' : 'false') + '; max-age=9999999';
}

function dectypeSelection() {
	return $("input:radio[name='position_types_allowed']:checked").val();
}

function onTrainHtmlLoad() {
		boardImageWrapper = $('#board_image_wrapper');
		boardImageWrapper.css('width', BOARD_WIDTH)
								.css('height', BOARD_HEIGHT);
		gnuId = $('#gnu_id span').text();
		initGraphics();
		readGnuIdAndDraw(gnuId);

		$('.undo').click(function(ev) {
			undo();
		});
		$('#invert_dice').click(function(ev) {
			invertDice();
		});
		$('#submit').click(submitHandler);
		$('#board').click(boardClickHandler);

		var checkboxIds = ['auto_submit', 'similar_pos'];
		for (var i = 0; i < checkboxIds.length; i++) {

			var checkboxId = checkboxIds[i];
			var idSelector = '#' + checkboxId;

			$(idSelector).click(checkboxId, function(eventObj) {checkboxHandler(eventObj.data)});

			if (new RegExp('\\b' + checkboxId + '=true\\b').test(document.cookie)) {
				$(idSelector).attr('checked', 'checked');
			}
			else {
				$(idSelector).removeAttr('checked');
			}
		}

		var dectypeMo = /\bdectype=(.*)\b/.exec(document.cookie);
		var dectype = 'either';
		if (dectypeMo) {
			dectype = dectypeMo[1];
		}

		$("input[value='" + dectype + "']").attr('checked', 'checked');


		$('#next_position').click(function() {
			var toNavigateTo = '/';
			if (new RegExp('\\b' + 'similar_pos' + '=true\\b').test(document.cookie)) {
				toNavigateTo += '?simtopid=' + encodeURIComponent(gnuId);
			}
			window.location = toNavigateTo;
		});

		$("input[name='position_types_allowed']").click(function() {
			document.cookie = 'dectype=' + dectypeSelection();
		});
}

